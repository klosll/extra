# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SacaLine(models.Model):
    _inherit = "saca.line"

    feed_family_id = fields.Many2one(
        string="Familia de Pienso",
        comodel_name="breeding.feed",
        related="breeding_id.feed_family",
        store=True,
    )

    estirpe_percentage = fields.Float(
        string="Estirpe (%)",
        compute="_compute_estirpe_percentage",
        store=True,
        group_operator="avg",
        digits="Weight Decimal Precision",
    )

    @api.depends("breeding_id", "breeding_id.lineage_percentage_ids")
    def _compute_estirpe_percentage(self):
        param_name = self.env["ir.config_parameter"].sudo().get_param(
            "klo_custom_mrp_descarga.nombre_estirpe", default="ROSS"
        )
        for line in self:
            percentage = 0.0
            if line.breeding_id and line.breeding_id.lineage_percentage_ids:
                lineage_rec = line.breeding_id.lineage_percentage_ids.filtered(
                    lambda r: r.lineage_id and r.lineage_id.name == param_name
                )
                if lineage_rec:
                    percentage = lineage_rec[0].percentage
            line.estirpe_percentage = percentage
