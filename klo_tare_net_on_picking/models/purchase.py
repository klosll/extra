# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools import OrderedSet


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fiscal_year_id = fields.Many2one('account.fiscal.year', string='Campaign', compute='_assign_fiscal_year', index=True)

    @api.depends('partner_id')
    def _assign_fiscal_year(self):
        campaigns = self.env['account.fiscal.year'].sudo().search([('date_from', '<=', self.date_order), ('date_to', '>=', self.date_order)])
        if campaigns:
            self.fiscal_year_id = campaigns.id


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    gross_weight = fields.Float('Gross weight', default=0.0, store=True, copy=False, digits='Gross Weight')
    tare_weight = fields.Float('Tare weight', default=0.0, store=True, digits='Tare Weight')
    net_weight = fields.Float('Net weight', compute='_clean_weight_calculate', default=0.0, copy=False, digits='Net Weight')
    humidity = fields.Float('Humidity', default=0.0, store=True)
    deduction = fields.Float('Deduction', compute='_clean_weight_calculate', default=0.0, store=True, digits='Deduction Weight')
    specific_weight = fields.Float('Specific weight', default=0.0, store=True, copy=False, digits='Specific Weight')

    @api.depends('gross_weight', 'humidity', 'tare_weight')
    @api.onchange('gross_weight', 'humidity', 'deduction')
    def _clean_weight_calculate(self):
        humidity_per = self.company_id.humidity_percent
        if not humidity_per:
            humidity_per = 0

        for po in self:
            po.net_weight = po.gross_weight - po.tare_weight

            if (po.humidity - humidity_per) > 0:
                po.deduction = po.net_weight * ((po.humidity - humidity_per) / 100)
            else:
                po.deduction = 0

            clean_weight = po.net_weight - po.deduction
            if clean_weight:
                po.product_qty = clean_weight
