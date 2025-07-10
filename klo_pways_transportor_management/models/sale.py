# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from datetime import datetime
from odoo.exceptions import UserError


class Sale(models.Model):
    _inherit = 'sale.order'

    remolque_id = fields.Many2one('fleet.vehicle', string="Remolque", copy=False)
    transporter_route_id = fields.Many2one('stock.transporter.route', string='Shipment Route',copy=False, required=False)


    def action_confirm(self):
        res = super(Sale, self).action_confirm()
        if self.transporter_id and self.transporter_id.trans_type == 'sale' and not self.create_trans:
            raise UserError("Por favor, actualiza la información de envío.")
        if self.picking_ids:
            fil_picking_ids = self.picking_ids.filtered(lambda x: x.state != 'cancel')
            fil_picking_ids.write({'transporter_id': self.transporter_id.id})
            if self.transporter_id.trans_type == 'sale' and fil_picking_ids:
                fil_picking_ids.create_transport_record(self.transporter_id)
                for pick in fil_picking_ids:
                    pick.write({
                        'remolque_id': self.remolque_id,
                    })
        return res
