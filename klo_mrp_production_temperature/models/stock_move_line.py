# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    temperature = fields.Float(
        string='Temperatura',
        digits=('Product Temperature', 2),
    )
