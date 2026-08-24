# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models


def _get_last_purchase_price_by_product(env, products):
    if not products:
        return {}
    lines = env['account.move.line'].sudo().search([
        ('product_id', 'in', products.ids),
        ('move_id.move_type', '=', 'in_invoice'),
        ('move_id.state', '=', 'posted'),
        ('exclude_from_invoice_tab', '=', False),
    ])
    # El ORM no permite ordenar por un campo de un modelo relacionado
    # (move_id.invoice_date); se ordena en Python: última factura primero.
    lines = lines.sorted(
        key=lambda line: (line.move_id.invoice_date or date.min, line.id),
        reverse=True,
    )
    result = {}
    for line in lines:
        result.setdefault(line.product_id.id, line.price_unit)
    return result


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    purchase_last_cost = fields.Float(
        string='Precio última compra',
        compute='_compute_purchase_last_cost',
        digits='Product Price',
    )

    @api.depends('product_id')
    def _compute_purchase_last_cost(self):
        prices = _get_last_purchase_price_by_product(
            self.env, self.mapped('product_id'))
        for lot in self:
            lot.purchase_last_cost = prices.get(lot.product_id.id, 0.0)
