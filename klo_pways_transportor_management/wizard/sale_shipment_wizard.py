from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaletShipmentWizard(models.TransientModel):
    _inherit = 'sale.shipment.wizard'
    _description ="Sale Report"

    remolque_id = fields.Many2one('fleet.vehicle', string="Remolque", copy=False)
    # KLO. Solo el conductor y vehículo son campos obligatorios.
    route = fields.Many2one('stock.transporter.route' , string='Route', required=False)
    pick_date = fields.Date(string='Picking Date',required=False)
    arrive_date = fields.Date(string='Arrival Date',required=False)
    picking_type = fields.Many2one('shipment.type', string='Type',required=False)


    # KLO. Añadimos el nuevo campo remolque_id del wizard al pedido.
    def create_transport_record(self):
        model = self.env.context.get('active_model')
        active_id = self.env[model].browse(self.env.context.get('active_id'))
        if not active_id.create_trans:
            active_id.write({
                'transporter_route_id': self.route.id,
                'vehicle_driver': self.driver.id,
                'vehicle_id': self.vehicle.id,
                'remolque_id': self.remolque_id,
                'pick_date': self.pick_date,
                'arrive_date':self.arrive_date,
                'picking_type':self.picking_type.id,
                'create_trans': True,
            })
        return True