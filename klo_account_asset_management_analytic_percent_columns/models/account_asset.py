# Copyright 2025 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountAsset(models.Model):

    _inherit = "account.asset"

    analytic_account_name = fields.Char(
        string="Nombre de Cuenta Analítica",
        compute="_compute_analytic_account_name",
        store=True
    )

    @api.depends('analytic_distribution')
    def _compute_analytic_account_name(self):
        for record in self:
            if record.analytic_distribution:
                # Extraer el primer ID de la distribución analítica
                analytic_account_id = next(iter(record.analytic_distribution.keys()), None)
                if analytic_account_id:
                    # Buscar el nombre de la cuenta analítica
                    analytic_account = self.env['account.analytic.account'].browse(int(analytic_account_id))
                    record.analytic_account_name = analytic_account.name if analytic_account else ""
                else:
                    record.analytic_account_name = ""
            else:
                record.analytic_account_name = ""
