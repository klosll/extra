from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_sort_lines_by_product_name(self):
        for picking in self:
            sorted_moves = picking.move_ids_without_package.sorted(
                key=lambda m: m.product_id.name or ""
            )
            for index, move in enumerate(sorted_moves, start=1):
                move.sequence = index

            sorted_move_lines = picking.move_line_ids.sorted(
                key=lambda ml: ml.product_id.name or ""
            )
            for index, move_line in enumerate(sorted_move_lines, start=1):
                move_line.sequence = index

        # Reload the form view to reflect the new order
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
