# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Fields
    use_sale_project = fields.Selection(
        string='Use Sale Project',
        related='company_id.use_sale_project',
        readonly=True,
    )
    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        ondelete='restrict',
    )

    # Compute and search fields, in the same order of fields declaration
    # Constraints and onchanges
    # Built-in methods overrides
    # Action methods

    def apply_project(self):
        for move in self:
            if not move.project_id:
                continue
            invoice_vals = move.project_id._prepare_invoice()
            move.write(invoice_vals)
            move.apply_project_product_lines()

    def apply_project_product_lines(self):
        for move in self:
            if not move.project_id:
                continue
            lines = self.env['account.move.line']
            for line in move.project_id.product_line_ids:
                invoice_line_vals = line._prepare_invoice_line(move.id)
                invoice_line = lines.new(invoice_line_vals)
                invoice_line.account_id = invoice_line._get_computed_account()
                invoice_line._onchange_currency()
                invoice_line._onchange_price_subtotal()
                lines |= invoice_line
            move.with_context(check_move_validity=False).line_ids = lines
            move.with_context(check_move_validity=False)._onchange_invoice_line_ids()

    # Business methods
