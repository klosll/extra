# -*- coding: utf-8 -*-

from odoo import models, fields, api


# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    shipping_sale_type = fields.Many2one(
        comodel_name='sale.order.type',
        string='Tipo pedido dir entrega',
        compute='_compute_shipping_sale_type',
        search='_search_shipping_sale_type',
        readonly=True,
        help='Tipo de pedido de venta de la dirección de entrega'
    )

    @api.depends('partner_shipping_id', 'partner_shipping_id.sale_type')
    def _compute_shipping_sale_type(self):
        """Obtiene el tipo de pedido de venta desde la dirección de entrega"""
        for record in self:
            if record.partner_shipping_id and hasattr(record.partner_shipping_id, 'sale_type'):
                record.shipping_sale_type = record.partner_shipping_id.sale_type
            else:
                record.shipping_sale_type = False

    def _search_shipping_sale_type(self, operator, value):
        """Permite buscar/filtrar por el tipo de pedido de la dirección de entrega"""
        partners = self.env['res.partner'].search([('sale_type', operator, value)])
        return [('partner_shipping_id', 'in', partners.ids)]
