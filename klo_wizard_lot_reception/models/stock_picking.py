# -*- coding: utf-8 -*-
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_lot_reception_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Capturar Lotes',
            'res_model': 'klo.lot.reception.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'active_id': self.id,
                'active_model': 'stock.picking',
            },
        }
