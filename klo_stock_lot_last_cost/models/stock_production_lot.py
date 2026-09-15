# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models


def _get_last_purchase_price_by_product(env, products):
    """Precio unitario de la línea del ÚLTIMO pedido de compra de cada producto.

    Se usa como valor de referencia para los quants sin lote.
    """
    if not products:
        return {}
    lines = env['purchase.order.line'].sudo().search([
        ('product_id', 'in', products.ids),
        ('state', 'in', ['purchase', 'done']),
    ])
    lines = lines.sorted(
        key=lambda line: (line.order_id.date_order or datetime.min, line.order_id.id),
        reverse=True,
    )
    result = {}
    for line in lines:
        result.setdefault(line.product_id.id, line.price_unit)
    return result


def _get_last_purchase_price_by_lot(env, lots):
    """Precio unitario de la línea del ÚLTIMO pedido de compra vinculado a cada
    lote, a través de sus movimientos de entrada de proveedor (incoming)."""
    result = {lot.id: 0.0 for lot in lots}
    if not lots:
        return result
    move_lines = env['stock.move.line'].sudo().search([
        ('lot_id', 'in', lots.ids),
        ('picking_code', '=', 'incoming'),
        ('state', '=', 'done'),
    ])
    lot_to_lines = {}
    for ml in move_lines:
        pol = ml.move_id.purchase_line_id
        if pol and pol.state in ('purchase', 'done'):
            lot_to_lines.setdefault(ml.lot_id.id, []).append(pol)
    for lot_id, pols in lot_to_lines.items():
        last = max(
            pols,
            key=lambda p: (p.order_id.date_order or datetime.min, p.order_id.id),
        )
        result[lot_id] = last.price_unit
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
        prices = _get_last_purchase_price_by_lot(self.env, self)
        for lot in self:
            lot.purchase_last_cost = prices.get(lot.id, 0.0)
