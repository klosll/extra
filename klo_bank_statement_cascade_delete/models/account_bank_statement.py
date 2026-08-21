# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def unlink(self):
        for statement in self:
            statement.line_ids.unlink()
        return super().unlink()
