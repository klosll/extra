# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLinePriceHistoryLine(models.TransientModel):
    _inherit = "sale.order.line.price.history.line"

    price_unit = fields.Float(
        related="sale_order_line_id.price_unit",
        min_display_digits="Product Price",
    )
