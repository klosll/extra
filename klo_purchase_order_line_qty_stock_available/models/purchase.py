from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_available = fields.Float(
        string="Stock actual",
        related="product_id.qty_available",
        readonly=True,
    )
