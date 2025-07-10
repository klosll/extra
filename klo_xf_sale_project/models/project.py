# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    # KLO. Redefinimos el campo invoice_ids del padre para que incluya las facturas que son de varios pedidos,
    # ya que la definición del padre (módulo xf_sale_project) solo acumula uno de los pedidos y el resto salen
    # sin factura asociada.
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string='Invoices',
        compute='_compute_invoice_ids',
        readonly=True,
    )

    # KLO. Se enlaza con las facturas relacionadas con los pedidos de origen de estas.
    def _compute_invoice_ids(self):
        for m in self:
            domain = [('sale_line_ids.order_id.project_id', '=', m.id)]
            m.invoice_ids = self.env['account.move.line'].search(domain, limit=1).move_id

    # KLO. A los datos que se rellenan de la clase padre se añade el de Plazos de pago que no se pasa por defecto.
    def _prepare_sale_order(self):
        sale_header_data = super()._prepare_sale_order()
        sale_header_data.update({
            'payment_term_id': self.partner_id.property_payment_term_id.id,
        })
        return sale_header_data


class ProjectProductLine(models.Model):
    _inherit = 'project.product.line'

    price_unit = fields.Monetary(
        string='Unit Price',
        compute='_compute_price_unit',
        digits='Product Price',
    )

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
            else:
                line.price_unit = line.product_id.lst_price
                self._get_discount()

    def _get_discount(self):
        for line in self:
            if not line.product_id:
                line.discount = 0.0
            else:
                product_pricelist_id = line.project_id.partner_id.property_product_pricelist.id
                product_tmpl_id = line.product_id.product_tmpl_id.id
                domain = [
                    ('product_tmpl_id', '=', product_tmpl_id),
                    ('pricelist_id', '=', product_pricelist_id)
                          ]
                product_discount = self.env['product.pricelist.item'].search(domain)
                if product_discount.compute_price == 'percentage':
                    if not line.discount:
                        line.discount = product_discount.percent_price
                else:
                    line.discount = 0.0


    # KLO. Adaptada del padre para quitar la línea de analytic_tag_ids
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
            'analytic_distribution': self.analytic_account_id.id,
        }
        # 'analytic_account_id': self.analytic_account_id.id,
        # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        if move_id:
            vals['move_id'] = move_id
        return vals

    # KLO. Adaptada del padre para quitar la línea de analytic_tag_ids
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
        }
        # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        if order:
            vals['order_id'] = order
        return vals
