# Copyright 2024 Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_packaging_price = fields.Float(string="Product packaging price", compute='_set_packaging_price', copy=False)

    @api.depends("product_packaging_qty")
    def _set_packaging_price(self):
        for po in self:
            pack_price = 0
            if po.product_packaging_qty != 0:
                pack_price = (po.quantity / po.product_packaging_qty) * po.price_unit

            po.product_packaging_price = pack_price
