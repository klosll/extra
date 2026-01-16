# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sales Order",
        compute="_compute_sale_order_id",
        store=True,
        index=True,
        copy=False,
    )

    project_id = fields.Many2one(
        comodel_name="project.project",
        related="sale_order_id.project_id",
        string="Project",
        store=True,
        copy=False,
        readonly=False,
    )

    @api.depends('invoice_line_ids.sale_line_ids')
    def _compute_sale_order_id(self):
        for move in self:
            sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
            move.sale_order_id = sale_orders[0] if sale_orders else False
