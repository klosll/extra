# -*- coding: utf-8 -*-
from pkg_resources import require

from odoo import models, fields, api , _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    remolque_id = fields.Many2one('fleet.vehicle', string="Remolque", copy=False)
    transporter_route_id = fields.Many2one('stock.transporter.route', string='Shipment Route', required=False)
