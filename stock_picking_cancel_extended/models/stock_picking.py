# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
#from _tkinter import create

class Picking(models.Model):
    _inherit = 'stock.picking'

    
    def action_cancel_draft(self):
        self.write({'state':'draft'})
        for move in self.move_ids_without_package :
            move.write({'state':'draft'})
        return

    def action_cancel(self):
        for picking in self :
            if picking.state == 'done':
                picking.mapped('move_lines').cancel_stock_picking()
                picking.move_lines.with_context(stock_cancel=True)._do_unreserve()
                for moves in picking.move_lines:
                    for line in moves.mapped('move_line_ids'):
                        line.result_package_id.unpack()
                    moves.mapped('move_line_ids').write({'qty_done': 0.0})
                picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()
                picking.mapped('move_lines')._action_cancel()
                picking.write({'is_locked': True})
                for move_lines in picking.move_ids_without_package:
                    qty1=0
                    product_obj_id = self.env['product.product'].search([('id','=',move_lines.product_id.id)])
                    qty1=product_obj_id.qty_available
                    update_product_qty=qty1 + move_lines.quantity_done
                    product_obj_id.update({
                        'qty_available': update_product_qty,
                    })
            else:
                picking.mapped('move_lines')._action_cancel()
                picking.write({'is_locked': True})
            account_move = self.env['account.move'].search([('ref','=',picking.name)])
            if account_move:
                account_move.button_cancel()
                account_move.sudo().unlink()