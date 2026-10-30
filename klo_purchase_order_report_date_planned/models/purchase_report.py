# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.tools.sql import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    date_planned = fields.Datetime('Scheduled Date', readonly=True)

    def _select(self) -> SQL:
        return SQL("%s, l.date_planned as date_planned", super()._select())
