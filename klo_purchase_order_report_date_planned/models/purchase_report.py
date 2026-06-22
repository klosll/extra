# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    date_planned = fields.Datetime('Scheduled Date', readonly=True)

    def _select(self):
        return super()._select() + """,
                    l.date_planned as date_planned"""
