# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .stock_production_lot import (
    _get_last_purchase_price_by_lot,
    _get_last_purchase_price_by_product,
)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    purchase_last_cost = fields.Float(
        string='Precio última compra',
        compute='_compute_purchase_last_cost',
        digits='Product Price',
    )
    purchase_last_value = fields.Float(
        string='Valor última compra',
        compute='_compute_purchase_last_cost',
        digits='Product Price',
    )

    @api.depends('lot_id', 'lot_id.purchase_last_cost', 'product_id', 'quantity')
    def _compute_purchase_last_cost(self):
        lots = self.mapped('lot_id')
        lot_prices = _get_last_purchase_price_by_lot(self.env, lots)
        no_lot = self.filtered(lambda q: not q.lot_id)
        product_prices = _get_last_purchase_price_by_product(
            self.env, no_lot.mapped('product_id'))
        for quant in self:
            if quant.lot_id:
                cost = lot_prices.get(quant.lot_id.id, 0.0)
            else:
                cost = product_prices.get(quant.product_id.id, 0.0)
            quant.purchase_last_cost = cost
            quant.purchase_last_value = cost * quant.quantity
