# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        # KLO: antes de generar los apuntes analíticos se retira la distribución
        # analítica que la aplicabilidad del plan no permite (p. ej. líneas con
        # cuentas de los grupos 438/217 en facturas de cliente).
        self.line_ids._klo_sanitize_analytic_distribution()
        return super()._post(soft=soft)
