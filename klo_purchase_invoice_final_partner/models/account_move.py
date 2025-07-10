# -*- coding: utf-8 -*-
"""Classes defining the populate factory for Journal Entries, Invoices and related models."""
from odoo import models, fields
from odoo.tools import populate

import logging
import math
from functools import lru_cache
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)

    def action_post(self):
        result = super(AccountMove, self).action_post()
        for analitic_line in self.analytic_line_ids:
            if self.sale_partner_id:
                analitic_line.partner_id = self.sale_partner_id
        return result
