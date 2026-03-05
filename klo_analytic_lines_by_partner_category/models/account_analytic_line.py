# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_category_ids = fields.Many2many(
        comodel_name='res.partner.category',
        string='Categorías del Contacto',
        compute='_compute_partner_category_ids',
        search='_search_partner_category_ids',
    )

    @api.depends('partner_id', 'partner_id.category_id')
    def _compute_partner_category_ids(self):
        for line in self:
            line.partner_category_ids = line.partner_id.category_id

    def _search_partner_category_ids(self, operator, value):
        partners = self.env['res.partner'].search([('category_id', operator, value)])
        return [('partner_id', 'in', partners.ids)]

