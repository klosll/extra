# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # KLO. Adaptada del padre para quitar las llamadas a funciones que no existen.
    def apply_project_product_lines(self):
        for move in self:
            if not move.project_id:
                continue
            lines = self.env['account.move.line']
            for line in move.project_id.product_line_ids:
                invoice_line_vals = line._prepare_invoice_line(move.id)
                invoice_line = lines.new(invoice_line_vals)
                # KLO. invoice_line.account_id = invoice_line._get_computed_account()
                # KLO. invoice_line._onchange_currency()
                # KLO. invoice_line._onchange_price_subtotal()
                lines |= invoice_line
            move.with_context(check_move_validity=False).line_ids = lines
            move.with_context(check_move_validity=False)._onchange_invoice_line_ids()

    # Business methods
