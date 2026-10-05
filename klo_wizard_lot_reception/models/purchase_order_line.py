# -*- coding: utf-8 -*-
from odoo import fields, models

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    surplus = fields.Boolean(string='Excedente', default=False)
