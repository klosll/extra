# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def unlink(self):
        self.mapped('line_ids').unlink()
        return super().unlink()
