# Copyright 2024 KLO Ingenieria Informática S.L.L. - Manuel Calomarde Gómez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    # KLO. Se redefine el Subtotal para guardar el dato y que aparezca la suma en las agrupaciones.
    price_subtotal = fields.Float("Subtotal", readonly=True, store=True)
    partner_id = fields.Many2one(
        related="contract_id.partner_id",
        string="Partner",
    )
