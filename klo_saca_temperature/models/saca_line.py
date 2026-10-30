# Copyright 2026 KLO Ingeniería Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SacaLine(models.Model):
    _inherit = "saca.line"

    temperature = fields.Float(
        string="Temperatura",
        digits=(16, 2),
    )