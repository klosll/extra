# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.project'

    # KLO. Nuevo campo analytic_account_id como cuenta analítica principal del proyecto.
    # Mismo tipo/relación/dominio/ondelete que el campo nativo account_id.
    # Se usa como cuenta analítica principal en pedidos/facturas generados desde el proyecto.
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Cuenta analítica',
        copy=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        ondelete='set null',
        help='Cuenta analítica principal del proyecto',
        groups='analytic.group_analytic_accounting',
    )

    # KLO. Campo temporal "Legacy" sin función, re-creado únicamente para evitar el
    # error "x_plan4_id field is undefined" provocado por referencias residuales
    # en la caché del navegador. NO se añade a ninguna vista. Se eliminará manualmente
    # una vez verificado que el cliente ya no lo referencia.
    x_plan4_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Legacy',
        copy=False,
        ondelete='set null',
    )

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
    # KLO. Usa analytic_account_id (nuevo campo) con fallback a account_id (campo nativo).
    def _prepare_sale_order(self):
        sale_header_data = super()._prepare_sale_order()
        sale_header_data.update({
            'payment_term_id': self.partner_id.property_payment_term_id.id,
        })
        # KLO. Sobrescribe analytic_account_id del padre (xf_sale_project usa self.analytic_account_id
        # que no existe en project.project nativo) con nuestro campo + fallback a account_id.
        analytic_account = self.analytic_account_id or self.account_id
        if analytic_account:
            sale_header_data['analytic_account_id'] = analytic_account.id
        else:
            sale_header_data.pop('analytic_account_id', None)
        return sale_header_data


class ProjectProductLine(models.Model):
    _inherit = 'project.product.line'

    # -------------------------------------------------------------------------
    # Helpers para compatibilidad Odoo 18 (pricelist sin discount_policy)
    # -------------------------------------------------------------------------

    def _get_pricelist(self):
        """Obtiene la lista de precios del partner del proyecto de forma segura.

        :return: recordset product.pricelist (puede estar vacío)
        :rtype: odoo.models.Model
        """
        self.ensure_one()
        partner = self.project_id.partner_id
        if not partner:
            return self.env['product.pricelist']
        pricelist = getattr(partner, 'property_product_pricelist', False)
        return pricelist if pricelist else self.env['product.pricelist']

    def _pricelist_shows_discount(self, pricelist=None):
        """Indica si la lista de precios muestra descuentos (Odoo 18 style).

        En Odoo 18 el campo `discount_policy` fue eliminado. Ahora se usa
        `product.pricelist.item._is_discount_feature_enabled()` que comprueba
        el grupo `sale.group_discount_per_so_line`, y `_show_discount()` que
        además requiere `compute_price == 'percentage'`.

        :param pricelist: recordset product.pricelist (opcional, usa _get_pricelist si no se pasa)
        :return: True si se debe mostrar descuento
        :rtype: bool
        """
        if pricelist is None:
            pricelist = self._get_pricelist()
        if not pricelist:
            return False
        # Obtener la regla aplicable para este producto
        rule_id = pricelist._get_product_rule(
            self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
        )
        if not rule_id:
            return False
        rule = self.env['product.pricelist.item'].browse(rule_id)
        return rule._show_discount()

    # -------------------------------------------------------------------------
    # Cálculo de precio de visualización (estilo sale.order.line Odoo 18)
    # -------------------------------------------------------------------------

    def _get_display_price(self, product):
        """Compute the displayed unit price for a given line (Odoo 18 style).

        Equivalente a `sale.order.line._get_display_price_ignore_combo`.
        Usa la regla de pricelist y `_show_discount` para decidir si aplicar
        descuento o devolver el precio final directamente.

        :param product: product.product record
        :return: precio unitario en la moneda del pricelist
        :rtype: float
        """
        self.ensure_one()
        pricelist = self._get_pricelist()
        if not pricelist or not product:
            return product.lst_price if product else 0.0

        # Obtener la regla de pricelist aplicable
        rule_id = pricelist._get_product_rule(
            product,
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
        )

        if not rule_id:
            # Sin regla -> precio de lista del producto en moneda del pricelist
            return pricelist._get_product_price(
                product,
                quantity=self.quantity or 1.0,
                uom=self.product_id.uom_id,
                date=self.project_id.date,
            )

        rule = self.env['product.pricelist.item'].browse(rule_id)

        # Precio final según pricelist (con descuento aplicado si corresponde)
        pricelist_price = rule._compute_price(
            product=product.with_context(**self._get_product_price_context()),
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
            currency=pricelist.currency_id,
        )

        # Si la regla no muestra descuento, devolver precio final directamente
        if not rule._show_discount():
            return pricelist_price

        # Calcular precio base (antes del descuento) para mostrar el descuento
        base_price = rule._compute_price_before_discount(
            product=product.with_context(**self._get_product_price_context()),
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
            currency=pricelist.currency_id,
        )

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_product_price_context(self):
        """Contexto para cálculo de precio del producto (atributos no variante, etc.)."""
        self.ensure_one()
        return self.product_id._get_product_price_context(
            self.product_id.product_template_attribute_value_ids
        )

    # -------------------------------------------------------------------------
    # Onchange de descuento (estilo sale.order.line._compute_discount Odoo 18)
    # -------------------------------------------------------------------------

    @api.onchange('product_id')
    def _onchange_discount(self):
        """Calcula el descuento automático basado en la regla de pricelist (Odoo 18 style).

        Equivalente a `sale.order.line._compute_discount`.
        Solo aplica si:
        - Existe producto, UoM, partner y pricelist
        - La feature de descuento está habilitada (grupo sale.group_discount_per_so_line)
        - La regla de pricelist es de tipo 'percentage' (_show_discount == True)
        """
        if not (self.product_id and self.product_id.uom_id and
                self.project_id.partner_id):
            return

        pricelist = self._get_pricelist()
        if not pricelist:
            return

        # Verificar si la feature de descuento está habilitada (Odoo 18)
        discount_enabled = self.env['product.pricelist.item']._is_discount_feature_enabled()
        if not discount_enabled:
            return

        # Obtener regla aplicable
        rule_id = pricelist._get_product_rule(
            self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
        )
        if not rule_id:
            self.discount = 0.0
            return

        rule = self.env['product.pricelist.item'].browse(rule_id)

        # Si la regla no muestra descuento, no aplicar ninguno
        if not rule._show_discount():
            self.discount = 0.0
            return

        # Calcular precios
        product_ctx = self.product_id.with_context(
            lang=self.project_id.partner_id.lang,
            partner=self.project_id.partner_id,
            quantity=self.quantity,
            date=self.project_id.date,
            pricelist=pricelist.id,
            uom=self.product_id.uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position'),
        )

        pricelist_price = rule._compute_price(
            product=product_ctx.with_context(**self._get_product_price_context()),
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
            currency=pricelist.currency_id,
        )

        base_price = rule._compute_price_before_discount(
            product=product_ctx.with_context(**self._get_product_price_context()),
            quantity=self.quantity or 1.0,
            uom=self.product_id.uom_id,
            date=self.project_id.date,
            currency=pricelist.currency_id,
        )

        if base_price != 0:
            discount = (base_price - pricelist_price) / base_price * 100
            if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                self.discount = discount
            else:
                self.discount = 0.0
        else:
            self.discount = 0.0

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return

        product = self.product_id
        if product:
            product_price = self._get_display_price(product)
            self.price_unit = product_price

    # KLO. Añadimos la cuenta analítica a la línea de pedido generada desde el proyecto.
    def _prepare_sale_order_line(self, order):
        sale_line_data = super()._prepare_sale_order_line(order)
        return sale_line_data