# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def _create_analytic_account_from_values(self, values):
        """Desactiva la creación automática de cuenta analítica al crear
        un proyecto con timesheets habilitados."""
        return self.env["account.analytic.account"].browse()

    def _create_analytic_account(self):
        """Desactiva la creación automática de cuenta analítica al habilitar
        timesheets en un proyecto existente."""
        return


