# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if not self.project_id:
            return
        if self.project_id.partner_id:
            self.partner_id = self.project_id.partner_id
        if self.project_id.analytic_account_id:
            self.analytic_account_id = self.project_id.analytic_account_id

    # Built-in methods overrides
    # Action methods

    def action_apply_project(self):
        self.apply_project()

    # Business methods

    def apply_project(self):
        for order in self:
            if not order.project_id:
                continue
            so_vals = order.project_id._prepare_sale_order()
            order.write(so_vals)
            order.apply_project_product_lines()

    def apply_project_product_lines(self):
        for order in self:
            if not order.project_id:
                continue
            lines = self.env['sale.order.line']
            for line in order.project_id.product_line_ids:
                so_line_vals = line._prepare_sale_order_line(order)
                so_line = lines.new(so_line_vals)
                lines |= so_line
            order.order_line = lines

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.project_id:
            invoice_vals['project_id'] = self.project_id.id
        return invoice_vals
