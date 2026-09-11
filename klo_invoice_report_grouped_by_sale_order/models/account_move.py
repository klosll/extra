# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = "account.move"

    def _sort_grouped_lines(self, lines_dic):
        def _sort_key(item):
            commitment_date = item["sale_order"].commitment_date
            is_note = item.get("is_last_section_notes", False)
            # Fecha de entrega de más reciente a más antigua. Sin fecha o
            # notas/secciones finales: al final de la lista.
            date_key = -commitment_date.toordinal() if commitment_date else 1
            return (date_key, is_note, item["sale_order"].name or "")

        return sorted(lines_dic, key=_sort_key)

    def _process_section_note_lines_grouped(
        self, previous_section, previous_note, lines_dic, sale_order=None
    ):
        for line in [previous_section, previous_note]:
            if line:
                key = (sale_order, line) if sale_order else line
                lines_dic.setdefault(key, 0.0)

    def _get_grouped_by_sale_order_sorted_lines(self):
        return self.invoice_line_ids.sorted(
            lambda ln: (-ln.sequence, ln.date, ln.move_name, -ln.id), reverse=True
        )

    def lines_grouped_by_sale_order(self):
        self.ensure_one()
        sale_order_dict = {}
        lines_dict = {}
        sale_order_obj = self.env["sale.order"]
        sign = (
            -1.0
            if self.move_type == "out_refund"
            and (
                not self.reversed_entry_id
                or self.reversed_entry_id.invoice_line_ids.mapped(
                    "sale_line_ids.order_id"
                )
                != self.invoice_line_ids.mapped("sale_line_ids.order_id")
            )
            else 1.0
        )
        previous_section = previous_note = False
        last_section_notes = []
        sorted_lines = self._get_grouped_by_sale_order_sorted_lines()

        for line in sorted_lines:
            if line.display_type in ["line_section", "line_note"]:
                if line.display_type == "line_section":
                    previous_section = line
                else:
                    previous_note = line
                last_section_notes.append(
                    {
                        "sale_order": sale_order_obj,
                        "line": line,
                        "quantity": 0.0,
                        "is_last_section_notes": True,
                    }
                )
                continue

            last_section_notes = []
            remaining_qty = line.quantity

            sale_orders = line.sale_line_ids.mapped("order_id")

            if sale_orders:
                for so in sale_orders:
                    key = (so, line)
                    self._process_section_note_lines_grouped(
                        previous_section, previous_note, sale_order_dict, so
                    )
                    so_lines = line.sale_line_ids.filtered(
                        lambda sl, so=so: sl.order_id == so
                    )
                    qty = min(
                        sum(so_lines.mapped("product_uom_qty")), remaining_qty
                    )
                    qty *= sign
                    sale_order_dict[key] = sale_order_dict.get(key, 0.0) + qty
                    remaining_qty -= abs(qty)
            else:
                key = (sale_order_obj, line)
                self._process_section_note_lines_grouped(
                    previous_section, previous_note, lines_dict
                )
                qty = line.quantity * sign
                sale_order_dict[key] = sale_order_dict.get(key, 0.0) + qty
                remaining_qty -= line.quantity

            remaining_qty = float_round(
                remaining_qty,
                precision_rounding=line.product_id.uom_id.rounding or 0.01,
            )
            if remaining_qty > 0:
                self._process_section_note_lines_grouped(
                    previous_section, previous_note, lines_dict
                )
                lines_dict[line] = remaining_qty

        no_sale_order = [
            {"sale_order": sale_order_obj, "line": key, "quantity": value}
            for key, value in lines_dict.items()
        ]
        with_sale_order = [
            {"sale_order": key[0], "line": key[1], "quantity": value}
            for key, value in sale_order_dict.items()
        ]
        return no_sale_order + self._sort_grouped_lines(
            with_sale_order + last_section_notes
        )
