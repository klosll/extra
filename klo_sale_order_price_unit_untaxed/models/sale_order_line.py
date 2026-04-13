# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_untaxed = fields.Float(
        string='Precio unitario (sin IVA)',
        compute='_compute_price_unit_untaxed',
        digits='Product Price',
        store=False,
    )

    @api.depends('price_unit', 'tax_id', 'product_id', 'currency_id', 'order_id.partner_id')
    def _compute_price_unit_untaxed(self):
        """Calcula el precio unitario sin impuestos.

        Usa compute_all de account.tax para extraer el precio base (total_excluded)
        a partir del precio unitario de la línea, que puede incluir IVA si los
        impuestos están configurados como 'precio incluido'.
        """
        for line in self:
            if line.tax_id:
                taxes_result = line.tax_id.compute_all(
                    line.price_unit,
                    currency=line.currency_id,
                    quantity=1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                line.price_unit_untaxed = taxes_result['total_excluded']
            else:
                line.price_unit_untaxed = line.price_unit

