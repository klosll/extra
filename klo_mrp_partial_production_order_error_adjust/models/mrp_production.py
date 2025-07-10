# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import operator as py_operator
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES


class MrpProduction(models.Model):
    _inherit = ['mrp.production']


    def _search_is_planned(self, operator, value):
        if operator not in ('=', '!='):
            raise UserError(_('Invalid domain operator %s', operator))

        if value not in (False, True):
            raise UserError(_('Invalid domain right operand %s', value))
        ops = {'=': py_operator.eq, '!=': py_operator.ne}
        ids = []
        for mo in self.search([]):
            if ops[operator](value, mo.is_planned):
                ids.append(mo.id)

        return [('id', 'in', ids)]


    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        elif not self.bom_id or self.bom_id.product_tmpl_id != self.product_tmpl_id or (self.bom_id.product_id and self.bom_id.product_id != self.product_id):
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id, bom_type='normal')
            if bom:
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id


    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if not self.product_id and self.bom_id:
            self.product_id = self.bom_id.product_id or self.bom_id.product_tmpl_id.product_variant_ids[:1]
        self.product_qty = self.bom_id.product_qty or 1.0
        self.product_uom_id = self.bom_id and self.bom_id.product_uom_id.id or self.product_id.uom_id.id
        self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)]
        self.move_finished_ids = [(2, move.id) for move in self.move_finished_ids]
        self.picking_type_id = self.bom_id.picking_type_id or self.picking_type_id


    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        source_location = self.location_src_id
        data = {
            'sequence': bom_line.sequence if bom_line else 10,
            'name': self.name,
            'date': self.date_planned_start,
            'date_deadline': self.date_planned_start,
            'bom_line_id': bom_line.id if bom_line else False,
            'picking_type_id': self.picking_type_id.id,
            'product_id': product_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.with_company(self.company_id).property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': operation_id,
            'price_unit': product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'state': 'draft',
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
        }
        return data


    def action_confirm(self):
        self._check_company()
        for production in self:
            if production.bom_id:
                production.consumption = production.bom_id.consumption
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            # In case of Serial number tracking, force the UoM to the UoM of product
            if production.product_tracking == 'serial' and production.product_uom_id != production.product_id.uom_id:
                production.write({
                    'product_qty': production.product_uom_id._compute_quantity(production.product_qty, production.product_id.uom_id),
                    'product_uom_id': production.product_id.uom_id
                })
                for move_finish in production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id):
                    move_finish.write({
                        'product_uom_qty': move_finish.product_uom._compute_quantity(move_finish.product_uom_qty, move_finish.product_id.uom_id),
                        'product_uom': move_finish.product_id.uom_id
                    })
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
            production.workorder_ids._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.move_raw_ids._trigger_scheduler()
        return True


    def _post_inventory(self, cancel_backorder=False):
        for order in self:
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do

            finish_moves = order.move_finished_ids.filtered(lambda m: m.product_id == order.product_id and m.state not in ('done', 'cancel'))
            # the finish move can already be completed by the workorder.
            if not finish_moves.quantity_done:
                finish_moves.quantity_done = float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP')
                finish_moves.move_line_ids.lot_id = order.lot_producing_id
            order._cal_price(moves_to_do)

            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish._action_done(cancel_backorder=cancel_backorder)
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('move_line_ids')
            order.move_finished_ids.move_line_ids.consume_line_ids = [(6, 0, consume_move_lines.ids)]
        return True


    def _generate_backorder_productions(self, close_mo=True):
        backorders = self.env['mrp.production']
        for production in self:
            if production.backorder_sequence == 0:  # Activate backorder naming
                production.backorder_sequence = 1
            production.name = self._get_name_backorder(production.name, production.backorder_sequence)
            backorder_mo = production.copy(default=production._get_backorder_mo_vals())
            if close_mo:
                production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
                    'raw_material_production_id': backorder_mo.id,
                })
                production.move_finished_ids.filtered(lambda m: m.state not in ('done', 'cancel')).write({
                    'production_id': backorder_mo.id,
                })
            else:
                new_moves_vals = []
                for move in production.move_raw_ids | production.move_finished_ids:
                    if not move.additional:
                        qty_to_split = move.product_uom_qty - move.unit_factor * production.qty_producing
                        qty_to_split = move.product_uom._compute_quantity(qty_to_split, move.product_id.uom_id, rounding_method='HALF-UP')
                        move_vals = move._split(qty_to_split)
                        if not move_vals:
                            continue
                        if move.raw_material_production_id:
                            move_vals[0]['raw_material_production_id'] = backorder_mo.id
                        else:
                            move_vals[0]['production_id'] = backorder_mo.id
                        new_moves_vals.append(move_vals[0])
                new_moves = self.env['stock.move'].create(new_moves_vals)
            backorders |= backorder_mo

            # We need to adapt `duration_expected` on both the original workorders and their
            # backordered workorders. To do that, we use the original `duration_expected` and the
            # ratio of the quantity really produced and the quantity to produce.
            ratio = production.qty_producing / production.product_qty
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder.duration_expected * ratio
            for workorder in backorder_mo.workorder_ids:
                workorder.duration_expected = workorder.duration_expected * (1 - ratio)

        # As we have split the moves before validating them, we need to 'remove' the excess reservation
        if not close_mo:
            self.move_raw_ids.filtered(lambda m: not m.additional)._do_unreserve()
            self.move_raw_ids.filtered(lambda m: not m.additional)._action_assign()
        # Confirm only productions with remaining components
        backorders.filtered(lambda mo: mo.move_raw_ids).action_confirm()
        backorders.filtered(lambda mo: mo.move_raw_ids).action_assign()

        # Remove the serial move line without reserved quantity. Post inventory will assigned all the non done moves
        # So those move lines are duplicated.
        backorders.move_raw_ids.move_line_ids.filtered(lambda ml: ml.product_id.tracking == 'serial' and ml.product_qty == 0).unlink()
        backorders.move_raw_ids._recompute_state()

        for production, backorder_mo in zip(self, backorders):
            first_wo = self.env['mrp.workorder']
            for old_wo, wo in zip(production.workorder_ids, backorder_mo.workorder_ids):
                wo.qty_produced = max(old_wo.qty_produced - old_wo.qty_producing, 0)
                if wo.product_tracking == 'serial':
                    wo.qty_producing = 1
                else:
                    wo.qty_producing = wo.qty_remaining
                if wo.qty_producing == 0:
                    wo.action_cancel()
                if not first_wo and wo.state != 'cancel':
                    first_wo = wo
            first_wo.state = 'ready'
        return backorders


    def button_mark_done(self):
        self._button_mark_done_sanity_checks()

        if not self.env.context.get('button_mark_done_production_ids'):
            self = self.with_context(button_mark_done_production_ids=self.ids)
        res = self._pre_button_mark_done()
        if res is not True:
            return res

        if self.env.context.get('mo_ids_to_backorder'):
            productions_to_backorder = self.browse(self.env.context['mo_ids_to_backorder'])
            productions_not_to_backorder = self - productions_to_backorder
            close_mo = False
        else:
            productions_not_to_backorder = self
            productions_to_backorder = self.env['mrp.production']
            close_mo = True

        self.workorder_ids.button_finish()

        backorders = productions_to_backorder._generate_backorder_productions(close_mo=close_mo)
        productions_not_to_backorder._post_inventory(cancel_backorder=True)
        productions_to_backorder._post_inventory(cancel_backorder=False)

        # if completed products make other confirmed/partially_available moves available, assign them
        done_move_finished_ids = (productions_to_backorder.move_finished_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda m: m.state == 'done')
        done_move_finished_ids._trigger_assign()

        # Moves without quantity done are not posted => set them as done instead of canceling. In
        # case the user edits the MO later on and sets some consumed quantity on those, we do not
        # want the move lines to be canceled.
        (productions_not_to_backorder.move_raw_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel')).write({
            'state': 'done',
            'product_uom_qty': 0.0,
        })

        for production in self:
            production.write({
                'date_finished': fields.Datetime.now(),
                'product_qty': production.qty_produced,
                'priority': '0',
                'is_locked': True,
            })

        for workorder in self.workorder_ids.filtered(lambda w: w.state not in ('done', 'cancel')):
            workorder.duration_expected = workorder._get_duration_expected()

        if not backorders:
            if self.env.context.get('from_workorder'):
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.production',
                    'views': [[self.env.ref('mrp.mrp_production_form_view').id, 'form']],
                    'res_id': self.id,
                    'target': 'main',
                }
            return True
        context = self.env.context.copy()
        context = {k: v for k, v in context.items() if not k.startswith('default_')}
        for k, v in context.items():
            if k.startswith('skip_'):
                context[k] = False
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'context': dict(context, mo_ids_to_backorder=None, button_mark_done_production_ids=None)
        }
        if len(backorders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': backorders[0].id,
            })
        else:
            action.update({
                'name': _("Backorder MO"),
                'domain': [('id', 'in', backorders.ids)],
                'view_mode': 'tree,form',
            })
        return action
