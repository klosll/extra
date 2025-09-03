# Copyright 2025 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    analytic_account_name = fields.Char(
        related='asset_id.analytic_account_name',
        string="Primera analítica",
        store=True
    )
