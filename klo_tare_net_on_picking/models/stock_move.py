# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.sql import column_exists, create_column


class StockMove(models.Model):
    _inherit = 'stock.move'

    mode_line_ids = fields.One2many('stock.move.line', 'move_id', check_company=True)
