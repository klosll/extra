# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import _, api, models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_partner_id = fields.Many2one(related='picking_id', string="Albarán", readonly=True)
