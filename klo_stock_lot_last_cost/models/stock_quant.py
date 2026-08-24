# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .stock_production_lot import _get_last_purchase_price_by_product


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

    @api.depends('product_id', 'quantity')
    def _compute_purchase_last_cost(self):
        prices = _get_last_purchase_price_by_product(
            self.env, self.mapped('product_id'))
        for quant in self:
            cost = prices.get(quant.product_id.id, 0.0)
            quant.purchase_last_cost = cost
            quant.purchase_last_value = cost * quant.quantity
