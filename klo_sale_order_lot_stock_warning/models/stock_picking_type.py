# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_stock_message = fields.Boolean(
        string="Mensaje de stock insuficiente de producto",
        default=False,
    )
