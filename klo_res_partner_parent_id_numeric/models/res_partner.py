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
            partner.parent_id_numeric = partner.parent_id.id if partner.parent_id else 0
