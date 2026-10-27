# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    @api.readonly
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # KLO. Si el contexto lo pide, listamos primero las empresas (compañías).
        if self.env.context.get('klo_company_first'):
            domain = expression.AND([[('display_name', operator, name)], args or []])
            records = self.search_fetch(
                domain, ['display_name'], limit=limit,
                order='is_company desc, parent_id.id nulls first, complete_name asc, id desc',
            )
            return [(record.id, record.display_name) for record in records.sudo()]
        return super().name_search(name, args, operator, limit)
