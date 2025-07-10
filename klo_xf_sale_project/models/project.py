# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

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

    def _get_display_price(self, product):
        # KLO. Esta función está traída de odoo/addons/sale/models/sale_order_line.py
        # Por si se necesita para un futuro por nuevo código.
        if self.project_id.partner_id.property_product_pricelist.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.project_id.partner_id.property_product_pricelist.id, uom=self.product_id.uom_id.id).price
        product_context = dict(self.env.context, partner_id=self.project_id.partner_id.id, date=self.project_id.date, uom=self.product_id.uom_id.id)

        final_price, rule_id = self.project_id.partner_id.property_product_pricelist.with_context(product_context).get_product_price_rule(product or self.product_id, self.quantity or 1.0, self.project_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.product_id.uom_po_id, self.project_id.partner_id.property_product_pricelist.id)
        if currency != self.project_id.partner_id.property_product_pricelist.currency_id:
            base_price = currency._convert(
                base_price, self.project_id.partner_id.property_product_pricelist.currency_id,
                self.project_id.company_id or self.env.company, self.project_id.date or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)


    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.project_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.project_id.company_id or self.env.company, self.project_id.date or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id


    @api.onchange('product_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_id.uom_id and
                self.project_id.partner_id and self.project_id.partner_id.property_product_pricelist and
                self.project_id.partner_id.property_product_pricelist.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.project_id.partner_id.lang,
            partner=self.project_id.partner_id,
            quantity=self.quantity,
            date=self.project_id.date,
            pricelist=self.project_id.partner_id.property_product_pricelist.id,
            uom=self.product_id.uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.project_id.partner_id.id, date=self.project_id.date, uom=self.product_id.uom_id.id)

        price, rule_id = self.project_id.partner_id.property_product_pricelist.with_context(product_context).get_product_price_rule(self.product_id, self.quantity or 1.0, self.project_id.partner_id)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.product_id.uom_id, self.project_id.partner_id.property_product_pricelist.id)

        if new_list_price != 0:
            if self.project_id.partner_id.property_product_pricelist.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.project_id.partner_id.property_product_pricelist,
                    self.project_id.company_id or self.env.company, self.project_id.date or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount


    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        product = self.product_id
        if product:
            product_price = self._get_display_price(product)
            self.price_unit = product_price
