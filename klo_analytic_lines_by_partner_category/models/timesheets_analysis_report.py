# -*- coding: utf-8 -*-
from odoo import fields, models


class TimesheetsAnalysisReport(models.Model):
    # KLO. El campo partner_category_ids se añade también al modelo del informe de
    # partes de horas porque su vista de búsqueda hereda de la búsqueda de apuntes
    # analíticos (donde sí existe el campo), evitando el error de "campo desconocido".
    _inherit = 'timesheets.analysis.report'

    partner_category_ids = fields.Many2many(
        comodel_name='res.partner.category',
        string='Categorías del Contacto',
        search='_search_partner_category_ids',
    )

    def _search_partner_category_ids(self, operator, value):
        partners = self.env['res.partner'].search([('category_id', operator, value)])
        return [('partner_id', 'in', partners.ids)]
