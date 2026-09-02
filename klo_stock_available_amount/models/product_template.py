# Copyright 2018 Camptocamp SA
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_amount = fields.Float(
        string="Qty Available Amount",
        compute="_compute_qty_available_amount",
    )

    # KLO. product.template no tiene stock_move_ids (solo product.product);
    # el campo se calcula on-demand al leerlo, sin @api.depends.
    def _compute_qty_available_amount(self):
        for prod in self:
            qty_amount = prod.qty_available * prod.standard_price
            prod.qty_available_amount = qty_amount
