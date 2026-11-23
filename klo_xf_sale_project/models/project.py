# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError

class Project(models.Model):
    _inherit = 'project.project'

    @api.model_create_multi
    def create(self, vals_list):
        default_account_id = self.default_get(['account_id']).get('account_id')
        if any(not vals.get('account_id', default_account_id) for vals in vals_list):
            raise ValidationError(_(
                "Debes seleccionar una cuenta analítica existente antes de crear el proyecto."
            ))
        return super().create(vals_list)

    def write(self, vals):
        if 'account_id' in vals and not vals['account_id']:
            raise ValidationError(_(
                "No puedes quitar la cuenta analítica de un proyecto."
            ))
        return super().write(vals)

    def _create_analytic_account(self):
        raise UserError(_(
            "La cuenta analítica debe crearse manualmente y seleccionarse en el proyecto."
        ))

    @api.model
    def _init_data_analytic_account(self):
        # No crear cuentas analíticas automáticamente al inicializar partes de horas.
        return True

    # KLO. Redefinimos el campo invoice_ids del padre para que incluya las facturas que son de varios pedidos,
    # ya que la definición del padre (módulo xf_sale_project) solo acumula uno de los pedidos y el resto salen
    # sin factura asociada.
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string='Invoices',
        compute='_compute_invoice_ids',
        readonly=True,
    )

    # KLO. Se enlaza con las facturas relacionadas con los pedidos de origen de estas.
    def _compute_invoice_ids(self):
        for m in self:
            domain = [('sale_line_ids.order_id.project_id', '=', m.id)]
            m.invoice_ids = self.env['account.move.line'].search(domain, limit=1).move_id

    # KLO. A los datos que se rellenan de la clase padre se añade el de Plazos de pago que no se pasa por defecto.
    def _prepare_sale_order(self):
        sale_header_data = super()._prepare_sale_order()
        sale_header_data.update({
            'payment_term_id': self.partner_id.property_payment_term_id.id,
        })
        return sale_header_data


class ProjectProductLine(models.Model):
    _inherit = 'project.product.line'

    # KLO. Regla de tarifa aplicable a la línea. Equivale a sale.order.line.pricelist_item_id
    # pero con la tarifa del partner del proyecto (no almacenada, se recalcula al cambiar
    # producto, uom, cantidad, tarifa o fecha del proyecto).
    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id',
        readonly=True,
    )

    @api.depends('product_id', 'product_uom_id', 'quantity', 'project_id.partner_id.property_product_pricelist', 'project_id.date')
    def _compute_pricelist_item_id(self):
        for line in self:
            pricelist = line.project_id.partner_id.property_product_pricelist
            if not line.product_id or not pricelist:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = pricelist._get_product_rule(
                    line.product_id,
                    quantity=line.quantity or 1.0,
                    uom=line.product_uom_id or line.product_id.uom_id,
                    date=line.project_id.date or fields.Date.today(),
                )

    def _get_pricelist_price(self):
        self.ensure_one()
        self.product_id.ensure_one()
        return self.pricelist_item_id._compute_price(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_uom_id or self.product_id.uom_id,
            date=self.project_id.date or fields.Date.today(),
            currency=self.currency_id or self.pricelist_item_id.currency_id,
        )

    def _get_pricelist_price_before_discount(self):
        self.ensure_one()
        self.product_id.ensure_one()
        return self.pricelist_item_id._compute_price_before_discount(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_uom_id or self.product_id.uom_id,
            date=self.project_id.date or fields.Date.today(),
            currency=self.currency_id or self.pricelist_item_id.currency_id,
        )

    def _get_display_price(self):
        # KLO. Esta función está traída de odoo/addons/sale/models/sale_order_line.py
        # (`_get_display_price_ignore_combo`), adaptada a la nueva API de tarifas de Odoo 18.
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if not self.pricelist_item_id._show_discount():
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    @api.onchange('product_id')
    def _onchange_discount(self):
        if not self.product_id or not self.pricelist_item_id:
            return
        if not self.env['product.pricelist.item']._is_discount_feature_enabled():
            return

        self.discount = 0.0

        if not self.pricelist_item_id._show_discount():
            # No pricelist rule was found for the product, therefore no discount to apply.
            return

        pricelist_price = self._get_pricelist_price()
        base_price = self._get_pricelist_price_before_discount()

        if base_price != 0:  # Avoid division by zero
            discount = (base_price - pricelist_price) / base_price * 100
            if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                # only show negative discounts if price is negative
                # otherwise it's a surcharge which shouldn't be shown to the customer
                self.discount = discount

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        self.price_unit = self._get_display_price()
        # KLO. Asignamos la moneda de la tarifa al campo currency_id para que el campo
        # Monetary price_unit se muestre en la moneda correcta al añadir el producto.
        pricelist = self.project_id.partner_id.property_product_pricelist
        if pricelist and pricelist.currency_id:
            self.currency_id = pricelist.currency_id
