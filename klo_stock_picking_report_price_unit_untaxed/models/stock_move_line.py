# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    price_unit_untaxed = fields.Float(
        string='Precio unitario (sin impuestos)',
        compute='_compute_price_unit_untaxed',
        min_display_digits='Product Price',
        store=False,
    )

    @api.depends('sale_line', 'product_uom_id', 'sale_line.price_unit_untaxed',
                 'sale_line.product_uom')
    def _compute_price_unit_untaxed(self):
        """Calcula el precio unitario sin impuestos de la línea de albarán.

        (i) Se aplica la misma conversión de unidad de medida que usa el OCA
        para `sale_price_unit`, de forma que ambos precios sean comparables
        en la unidad del movimiento.

        (ii) El valor base proviene del campo `price_unit_untaxed` de
        `sale.order.line`, aportado por `klo_sale_order_price_unit_untaxed`:
        es el precio unitario sin redondeo y sin impuestos.

        (iii) `min_display_digits='Product Price'` imita el campo `price_unit`
        del core: al renderizar con `t-field` se muestran los mismos decimales
        que en el formulario y sin símbolo de moneda.
        """
        for line in self:
            if not line.sale_line:
                line.price_unit_untaxed = 0.0
                continue
            line.price_unit_untaxed = line.sale_line.product_uom._compute_price(
                line.sale_line.price_unit_untaxed, line.product_uom_id)
