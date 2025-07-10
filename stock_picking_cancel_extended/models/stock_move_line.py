# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
#from _tkinter import create


class stock_move_line(models.Model):
    _inherit = "stock.move.line"

    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for ml in self:
            if self._context.get('stock_cancel') == False and ml.state =='done':
                if ml.state in ('done', 'cancel'):
                    raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
                # Unlinking a move line should unreserve.
                if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
                    try:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        if ml.lot_id:
                            self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                        else:
                            raise
            elif self._context.get('stock_cancel') == True and ml.state =='done':
                if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
                    try:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        if ml.lot_id:
                            self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                        else:
                            raise
        moves = self.mapped('move_id')
        for move in moves:
            if self._context.get('stock_cancel') == False and move.state != 'done':
                res = super(stock_move_line, self).unlink()
            else:
                res = True
            if self._context.get('stock_cancel') == True and move.state != 'done':
                res = super(stock_move_line, self).unlink()
            if moves:
                moves._recompute_state()
            return res