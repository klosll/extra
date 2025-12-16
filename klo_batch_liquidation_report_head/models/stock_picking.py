# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def lines_grouped_by_product(self):
        self.ensure_one()
        lines_dict = OrderedDict()      
        move_lines = self.mapped("move_line_ids_without_package")
        move_lines = move_lines.sorted(lambda ln: (ln.product_id.name, -ln.id), reverse=True)
        for line in move_lines:
            key = (line.product_id.id, line.product_packaging_id.id if line.product_packaging_id else 0)
            if key not in lines_dict:
                lines_dict[key] = {
                    "move_name": line.move_id.name,
                    "container": line.container,
                    "packaging_name": (
                        line.product_packaging_id.name if line.product_packaging_id else ""
                    ),          
                    "packaging_qty": line.product_packaging_qty,
                    "qty_done": line.qty_done,
                    "uom_name": line.product_uom_id.name
                }
            else:
                lines_dict[key]["packaging_qty"] += line.product_packaging_qty
                lines_dict[key]["qty_done"] += line.qty_done
        lines_dict = list(lines_dict.values())
        return lines_dict
