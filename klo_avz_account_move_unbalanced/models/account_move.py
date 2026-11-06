# Copyright (c) 2021 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    unbalance = fields.Boolean(string="Not balanced")

    @contextmanager
    def _check_balanced(self, container):
        # Moves flagged as `unbalance` are exempt from the balanced check,
        # like in the previous version of this method.
        container = dict(
            container,
            records=container["records"].filtered(lambda move: not move.unbalance),
        )
        with super(AccountMove, self)._check_balanced(container):
            yield
