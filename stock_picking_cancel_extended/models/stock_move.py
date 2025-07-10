# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, OrderedSet
#from _tkinter import create


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _do_unreserve(self):
        moves_to_unreserve = self.env['stock.move']        
        for move in self:
            if self._context.get('stock_cancel') == True:
                if move.state == 'cancel':
                    # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
                    continue
                if move.state == 'done':
                    if move.scrapped:
                        # We may have done move in an open picking in a scrap scenario.
                        continue
            else:
                if move.state == 'cancel':
                    # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
                    continue
                if move.state == 'done':
                    if move.scrapped:
                        # We may have done move in an open picking in a scrap scenario.
                        continue
                    else:
                        raise UserError(_('You cannot unreserve a stock move that has been set to \'Done\'.'))
            moves_to_unreserve |= move
        moves_to_unreserve.mapped('move_line_ids').with_context(stock_cancel=True).unlink()
        return True


    def cancel_stock_picking(self):
        for move in self:
            if  move.stock_valuation_layer_ids:
                move.stock_valuation_layer_ids.sudo().unlink()
                if move.product_id.cost_method in ('average', 'fifo'):
                    last_valuation = self.env['stock.valuation.layer'].search([('product_id', '=', move.product_id.id),('remaining_qty','!=',0.0)], order="id ASC", limit=1)
                    last_valuation.remaining_qty = last_valuation.quantity

            move.with_context(stock_cancel=True)._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
            if move.quantity_done:
                if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                    for move_id in move:
                        for line in move_id.move_line_ids:                                  
                            if move.location_dest_id.usage == 'customer':
                                if line.product_id.tracking == 'lot' or line.product_id.tracking == 'serial':
                                    
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',line.product_id.id),('location_id','=',line.location_dest_id.id), ('lot_id', '=', line.lot_id.id)])
                                    stock_quant = self.env['stock.quant'].sudo().search([('product_id','=',line.product_id.id),('location_id','=',line.location_id.id), ('lot_id', '=', line.lot_id.id)])
                                    if not stock_quant:
                                        stock_quant = self.env['stock.quant'].sudo().search([('product_id','=',line.product_id.id),('location_id','=',line.location_id.id)])
                                        
                                        
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity
                                        outgoing_quant[0].quantity = old_qty - line.qty_done
                                        abc = outgoing_quant[0].quantity
                                    if stock_quant:
                                        old_qty = stock_quant[0].quantity
                                        stock_quant[0].quantity = old_qty + line.qty_done
                                        
                                else:
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                    stock_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity
                                        outgoing_quant[0].quantity = old_qty - move.product_uom_qty
                                        abc = outgoing_quant[0].quantity
                                    if stock_quant:
                                        old_qty = stock_quant[0].quantity
                                        stock_quant[0].quantity = old_qty + move.product_uom_qty
                            else:
                                if line.product_id.tracking != 'lot':
                                    outgoing_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                    if outgoing_customer_quant:
                                        old_qty = outgoing_customer_quant[0].quantity
                                        outgoing_customer_quant[0].quantity = old_qty - move.product_uom_qty
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity                                    
                                        outgoing_quant[0].quantity = old_qty + move.product_uom_qty
                                    else:
                                        vals = { 'product_id' :move.product_id.id,
                                                 'location_id':move.location_id.id,
                                                 'quantity': move.product_uom_qty,
                                               }
                                        test = self.env['stock.quant'].sudo().create(vals)
                                else:
                                    outgoing_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
                                    if outgoing_customer_quant:
                                        old_qty = outgoing_customer_quant[0].quantity
                                        outgoing_customer_quant[0].quantity = old_qty - move.product_uom_qty
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity                                    
                                        outgoing_quant[0].quantity = old_qty + move.product_uom_qty
                                    else:
                                        vals = { 'product_id' :move.product_id.id,
                                                 'location_id':move.location_id.id,
                                                 'quantity': move.product_uom_qty,
                                                 'lot_id':line.lot_id.id,
                                               }
                                        test = self.env['stock.quant'].sudo().create(vals)                                  
                                        
                if move.picking_id.picking_type_id.code == 'incoming':
                    for move_id in move:
                        for line in move_id.move_line_ids:
                            if line.lot_id:
                                if line.product_id.tracking == 'lot':
                                    incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
                                    incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
                                    if incoming_quant:
                                        old_qty = incoming_quant[0].quantity
                                        incoming_quant[0].quantity = old_qty - move.product_uom_qty
                                    if incoming_customer_quant:
                                        old_qty = incoming_customer_quant[0].quantity
                                        incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty
                                else:
                                    incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
                                    for lot in incoming_quant:
                                        old_qty = lot.quantity
                                        lot.unlink()
                                        vals = { 'product_id' :move.product_id.id,
                                                 'location_id':move.location_dest_id.id,
                                                 'quantity': old_qty,
                                                 'lot_id':line.lot_id.id,
                                               }
                                        test = self.env['stock.quant'].sudo().create(vals)
                            else:
                                incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                if incoming_quant:
                                    old_qty = incoming_quant[0].quantity
                                    incoming_quant[0].quantity = old_qty - move.product_uom_qty
                                incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                if incoming_customer_quant:
                                    old_qty = incoming_customer_quant[0].quantity
                                    incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty

            account_move = self.env['account.move'].sudo().search([('stock_move_id','=',move.id)],order="id desc", limit=1)
            if account_move : 
                account_move.button_cancel()
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True    