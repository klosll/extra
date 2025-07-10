# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     tare_weight = fields.Float('Tare weight', default=0.0, store=True, copy=False, digits='Tare Weight')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    gross_weight = fields.Float('Gross weight', default=0.0, store=True, copy=False, digits='Gross Weight')
    tare_weight = fields.Float('Tare weight', default=0.0, store=True, copy=False, digits='Tare Weight')
    net_weight = fields.Float('Net weight', compute='_clean_weight_calculate', default=0.0, store=True, copy=False, digits='Net Weight')
    move_ids = fields.One2many('stock.move', 'sale_line_id', check_company=True)

    @api.depends("gross_weight","tare_weight")
    def _clean_weight_calculate(self):
        for po in self:
            po.net_weight = po.gross_weight - po.tare_weight
            if po.net_weight:
                po.product_uom_qty = po.net_weight
