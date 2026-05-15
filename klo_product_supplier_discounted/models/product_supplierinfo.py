# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discounted_price = fields.Float(
        string="Precio con dto.",
        digits="Product Price",
        compute="_compute_discounted_price",
        store=True,
        help="Precio resultante de aplicar los 3 descuentos sobre el precio de compra.",
    )

    @api.depends("price", "discount1", "discount2", "discount3")
    def _compute_discounted_price(self):
        for record in self:
            discounts = [record.discount1 or 0.0, record.discount2 or 0.0, record.discount3 or 0.0]
            # Mismo método que purchase.triple.discount.mixin._get_aggregated_multiple_discounts
            discount_factors = [1 - (d / 100.0) for d in discounts]
            aggregated_factor = functools.reduce(lambda x, y: x * y, discount_factors)
            record.discounted_price = record.price * aggregated_factor

