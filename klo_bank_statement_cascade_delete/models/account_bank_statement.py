# -*- coding: utf-8 -*-
from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def unlink(self):
        for statement in self:
            statement.line_ids.unlink()
        return super().unlink()
