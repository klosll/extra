# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, MissingError


class Project(models.Model):
    _inherit = 'project.project'

    # Fields

    product_line_ids = fields.One2many(
        string='Product Lines',
        comodel_name='project.product.line',
        inverse_name='project_id',
    )
    sale_order_ids = fields.One2many(
        string='Sale Orders',
        comodel_name='sale.order',
        inverse_name='project_id',
        readonly=True,
    )
    sale_order_ids_count = fields.Integer(
        compute='_compute_sale_order_ids_count',
        compute_sudo=True,
    )
    invoice_ids = fields.One2many(
        string='Invoices',
        comodel_name='account.move',
        inverse_name='project_id',
        readonly=True,
    )
    invoice_ids_count = fields.Integer(
        compute='_compute_invoice_ids_count',
        compute_sudo=True,
    )

    # Compute and search fields, in the same order of fields declaration

    @api.depends('sale_order_ids')
    def _compute_sale_order_ids_count(self):
        for record in self.sudo():
            record.sale_order_ids_count = len(record.sale_order_ids)

    @api.depends('invoice_ids')
    def _compute_invoice_ids_count(self):
        for record in self.sudo():
            record.invoice_ids_count = len(record.invoice_ids)

    # Constraints and onchanges
    # Built-in methods overrides
    # Action methods
    def action_create_sale_order(self):
        self.ensure_one()
        sale_order_vals = self._prepare_sale_order()
        sale_order = self.env['sale.order'].create(sale_order_vals)
        sale_order.apply_project_product_lines()
        return self.action_view_sale_orders()

    def action_view_sale_orders(self):
        self.ensure_one()
        action = {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        if self.sale_order_ids_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_order_ids.id,
            })
        else:
            action.update({
                'name': _("Sale Order related to the project %s", self.name),
                'domain': [('id', 'in', self.sale_order_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def action_view_invoices(self, invoices=False):
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the project, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        act_window_close = {'type': 'ir.actions.act_window_close'}
        action = self.env['ir.actions.actions']._for_xml_id("account.action_move_out_invoice_type")
        # choose the view_mode accordingly
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = act_window_close

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_project_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    # Business methods

    def _prepare_sale_order(self):
        self.ensure_one()
        return {
            'project_id': self.id,
            'analytic_account_id': self.analytic_account_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
        }

    def _prepare_invoice(self):
        self.ensure_one()
        return {
            'move_type': 'out_invoice',
            'project_id': self.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
        }


class ProjectProductLine(models.Model):
    _name = 'project.product.line'
    _description = 'Project Product Line'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        related='project_id.company_id',
        readonly=True,
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    product_uom_category_id = fields.Many2one(
        comodel_name='uom.category',
        related='product_id.uom_id.category_id',
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        string='Unit of Measure',
        comodel_name='uom.uom',
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    name = fields.Char(
        string='Label',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        digits='Product Unit of Measure',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )
    price_unit = fields.Monetary(
        string='Unit Price',
        digits='Product Price',
    )
    discount = fields.Float(
        string='Discount (%)',
        digits='Discount',
        default=0.0,
    )
    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
        check_company=True,
    )
    analytic_tag_ids = fields.Many2many(
        string='Analytic Tags',
        comodel_name='account.analytic.tag',
        check_company=True,
    )

    def _prepare_invoice_line(self, move_id):
        self.ensure_one()
        vals = {
            'display_type': False,
            'partner_id': self.project_id.partner_id.id,
            'company_id': self.project_id.company_id.id,
            'currency_id': self.currency_id.id,
            'sequence': self.sequence,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'name': self.name,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        if move_id:
            vals['move_id'] = move_id
        return vals

    def _prepare_sale_order_line(self, order):
        self.ensure_one()
        if not self.product_id:
            raise MissingError(_('Please set product for each project product line as is required to generate sale orders'))
        vals = {
            'name': self.name,
            'sequence': self.sequence,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uom_id.id or self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        if order:
            vals['order_id'] = order
        return vals
