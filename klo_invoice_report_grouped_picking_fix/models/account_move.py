# Copyright 2026 KLO Ingenieria Informatica S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _process_section_note_lines_grouped(
        self, previous_section, previous_note, lines_dic, pick_order=None
    ):
        """Processes section and note lines, grouping them by order.

        Override to prevent section/note lines from being added to
        multiple pickings when several pickings have product lines
        after the same section/note.
        """
        for line in [previous_section, previous_note]:
            if line:
                already_added = any(
                    (isinstance(k, tuple) and k[1].id == line.id)
                    or (not isinstance(k, tuple) and k.id == line.id)
                    for k in lines_dic
                )
                if not already_added:
                    key = (pick_order, line) if pick_order else line
                    lines_dic.setdefault(key, 0.0)
