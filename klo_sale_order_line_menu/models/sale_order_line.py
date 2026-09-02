# Copyright 2023 Moduon Team
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
    # KLO. En v18 sale.order ya no tiene analytic_account_id (se usa analytic_distribution),
    # por lo que se elimina el campo relacionado account_analytic_id que existía en v15.
    product_categ_id = fields.Many2one(related='product_id.categ_id', string='Product Category', readonly=True)
