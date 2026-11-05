# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BatchMovementDetailWizard(models.TransientModel):
    _name = "batch.movement.detail.wizard"
    _description = "Asistente para el detalle de existencias crianzas/madres"

    date = fields.Date(
        string="Fecha hasta",
        required=True,
        default=fields.Date.today,
        help="Se exportarán los movimientos validados hasta esta fecha.",
    )

    def button_create_report(self):
        data = {"date": fields.Date.to_string(self.date)}
        if "active_ids" in self.env.context:
            data.update({"objects": self.env.context.get("active_ids")})
        return self.env.ref(
            "klo_batch_movement_detail_report.action_batch_movement_detail_xlsx"
        ).report_action(self, data=data)
