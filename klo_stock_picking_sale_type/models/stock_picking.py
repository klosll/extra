# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    sale_type = fields.Many2one(
        comodel_name='sale.order.type',
        string='Tipo pedido',
        compute='_compute_sale_type',
        search='_search_sale_type',
        store=True,
        readonly=True,
        help='Tipo de pedido de venta del pedido de venta relacionado'
    )

    @api.depends('partner_id', 'partner_id.sale_type')
    def _compute_sale_type(self):
        """Obtiene el tipo de pedido de venta desde el pedido de venta relacionado"""
        for record in self:
            if record.partner_id and hasattr(record.partner_id, 'sale_type'):
                record.sale_type = record.partner_id.sale_type
            else:
                record.sale_type = False
