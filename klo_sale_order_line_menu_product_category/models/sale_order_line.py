# Copyright 2023 Moduon Team
# Copyright (C) 2026 KLO Ingeniería Informática S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(
        related="order_id.date_order",
        readonly=True,
        store=True,
        index=True,
    )
    product_categ_id = fields.Many2one(related='product_id.categ_id', string='Product Category', readonly=True)