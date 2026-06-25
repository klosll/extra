from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_sort_lines_by_product_name(self):
        for order in self:
            sorted_lines = order.order_line.sorted(
                key=lambda l: l.product_id.name or ""
            )
            for index, line in enumerate(sorted_lines, start=1):
                line.sequence = index
