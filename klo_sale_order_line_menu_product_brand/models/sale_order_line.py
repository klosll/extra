# Copyright 2023 Moduon Team
# Copyright (C) 2026 KLO Ingeniería Informática S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_brand_id = fields.Many2one(related='product_id.product_brand_id', string='Product Brand', readonly=True)
