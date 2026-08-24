# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models


def _get_last_purchase_price_by_product(env, products):
    if not products:
        return {}
    lines = env['purchase.order.line'].sudo().search([
        ('product_id', 'in', products.ids),
        ('state', 'in', ['purchase', 'done']),
    ])
    # El ORM no permite ordenar por un campo de un modelo relacionado
    # (order_id.date_order); se ordena en Python: último pedido primero.
    lines = lines.sorted(
        key=lambda line: (line.order_id.date_order or datetime.min, line.order_id.id),
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
