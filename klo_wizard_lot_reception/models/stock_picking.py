# -*- coding: utf-8 -*-
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_lot_reception_wizard(self):
        self.ensure_one()
        wizard = self.env['klo.lot.reception.wizard'].search(
            [('picking_id', '=', self.id)], limit=1
        )
        if not wizard:
            wizard = self.env['klo.lot.reception.wizard'].create({
                'picking_id': self.id,
            })
        context = {}
        if self.state != 'done':
            context['form_view_initial_mode'] = 'edit'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Capturar Lotes',
            'res_model': 'klo.lot.reception.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'current',
            'context': context,
        }
