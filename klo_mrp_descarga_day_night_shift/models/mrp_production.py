# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    turno = fields.Selection(
        string="Turno",
        selection=[
            ("dia", "Día"),
            ("noche", "Noche"),
        ],
        help="Turno de despiece: Día o Noche",
    )


