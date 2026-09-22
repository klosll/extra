# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_report_line_name(self):
        self.ensure_one()
        if not self.name:
            return ""
        parts = self.name.split("\n", 1)
        first = re.sub(r'^\s*\[[^\]]*\]\s*', '', parts[0])
        if len(parts) > 1:
            return first + "\n" + parts[1]
        return first