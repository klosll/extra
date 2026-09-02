# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Project(models.Model):
    _inherit = "project.project"

    # KLO: desactiva la creación automática de cuenta analítica. En v18 la
    # creación tanto en create() como en write() de hr_timesheet se canaliza
    # por _get_values_analytic_account_batch; devolver lista vacía cancela
    # ambos caminos sin llamar a super() (intención: cancelar el padre).
    @api.model
    def _get_values_analytic_account_batch(self, project_vals_list):
        return []

    def _create_analytic_account(self):
        # KLO: cancela la creación automática al habilitar timesheets en un
        # proyecto existente (no se llama a super()).
        return
