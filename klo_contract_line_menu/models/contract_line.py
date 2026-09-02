# Copyright 2024 KLO Ingenieria Informática S.L.L. - Manuel Calomarde Gómez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    # KLO. En v18 partner_id y price_subtotal ya son campos stored en contract.line
    # (partner_id se redefine con store=True en el propio OCA contract, y
    # price_subtotal es Monetary stored en contract.template.line). Por tanto no
    # es necesario redefinirlos aquí como se hacía en v15.
