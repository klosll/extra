# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    # KLO: en v15 el informe de partes de horas se basaba en account.analytic.line y
    # permitía desplegar las horas por cuenta analítica dentro de cada empleado.
    # En v18 el informe usa el modelo timesheets.analysis.report (vista SQL sobre
    # account_analytic_line) que no expone la columna account_id, por lo que no se
    # puede agrupar por ella. Se añade el campo y su columna en la vista SQL.
    _inherit = "timesheets.analysis.report"

    account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Cuenta analítica",
        readonly=True,
    )

    @api.model
    def _select(self):
        return super()._select() + """,
            A.account_id AS account_id
        """
