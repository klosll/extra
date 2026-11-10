# Copyright 2026 KLO Ingenieria Informatica S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    parent_id_numeric = fields.Integer(
        string="ID Empresa",
        compute="_compute_parent_id_numeric",
        store=False,
    )

    @api.depends("parent_id")
    def _compute_parent_id_numeric(self):
        for partner in self:
            # Empresa padre si existe; en caso contrario, el propio ID del contacto
            partner.parent_id_numeric = partner.parent_id.id if partner.parent_id else partner.id or 0
