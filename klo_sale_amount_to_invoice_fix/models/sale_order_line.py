# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "discount",
        "price_total",
        "product_uom_qty",
        "qty_delivered",
        "qty_invoiced_posted",
    )
    def _compute_amount_to_invoice(self):
        res = super()._compute_amount_to_invoice()
        for line in self:
            if line.product_uom_qty or not line.qty_invoiced_posted:
                continue
            inv_lines = line._get_invoice_lines().filtered(
                lambda l: l.move_id.state == "posted"
                or l.move_id.payment_state == "invoicing_legacy"
            )
            if not inv_lines:
                continue
            amount_invoiced = sum(
                inv_line.price_total * -inv_line.move_id.direction_sign
                for inv_line in inv_lines
            )
            unit_price_total = amount_invoiced / line.qty_invoiced_posted
            uom_qty_to_consider = (
                line.qty_delivered
                if line.product_id.invoice_policy == "delivery"
                else 0
            )
            qty_to_invoice = uom_qty_to_consider - line.qty_invoiced_posted
            line.amount_to_invoice = unit_price_total * qty_to_invoice
        return res
