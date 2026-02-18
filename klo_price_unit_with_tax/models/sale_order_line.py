# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_with_tax = fields.Monetary(
        string='Unit Price with Tax',
        compute='_compute_price_unit_with_tax',
        store=True,
        readonly=True,
        currency_field='currency_id',
        help='Unit price including taxes'
    )

    @api.depends('price_unit', 'tax_id', 'product_uom_qty', 'discount', 'order_id.partner_id')
    def _compute_price_unit_with_tax(self):
        """
        Compute unit price with taxes included.
        Uses the same logic as price_total calculation but divides by quantity.
        """
        for line in self:
            if line.product_uom_qty:
                # Prepare base line for tax computation
                base_line = line._prepare_base_line_for_taxes_computation()
                self.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)

                # Calculate price with tax per unit
                price_total = base_line['tax_details']['raw_total_included_currency']
                line.price_unit_with_tax = price_total / line.product_uom_qty
            else:
                line.price_unit_with_tax = line.price_unit

