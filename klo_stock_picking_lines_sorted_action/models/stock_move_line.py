from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _order = "sequence, result_package_id desc, id"
