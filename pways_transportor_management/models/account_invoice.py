# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    transporter_id = fields.Many2one('res.partner', string="Transporter")

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    transporter_id = fields.Many2one('res.partner', string='Transporter')
