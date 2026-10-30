# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Neto = precio unitario sin impuestos con el descuento aplicado. Se define con
    # min_display_digits='Product Price' (sin digits) para MIMETIZAR el campo
    # price_unit del core: el render QWeb con t-field le aplica los mismos decimales
    # que el campo "Precio unitario" del formulario (precisión decimal "Product
    # Price"). El valor se mantiene SIN redondear (el redondeo lo hace la
    # presentación). El Importe del informe muestra sale_price_subtotal (subtotal de
    # Odoo del albarán) para cuadrar exactamente con el Untaxed Amount del pie; este
    # campo price_unit_net se usa para la columna Neto (y su cálculo manual Cantidad
    # × Neto puede diferir ±0,01 € con impuestos precio incluido).
    price_unit_net = fields.Float(
        string='Neto',
        compute='_compute_price_unit_net',
        min_display_digits='Product Price',
        store=False,
    )

    @api.depends('price_unit_untaxed', 'sale_discount')
    def _compute_price_unit_net(self):
        for line in self:
            line.price_unit_net = line.price_unit_untaxed * (
                1 - (line.sale_discount or 0.0) / 100.0)
