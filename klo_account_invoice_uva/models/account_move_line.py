# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    grado = fields.Float(
        string='Grado',
        digits=(16, 2),
        default=0.0,
    )
    kilos = fields.Float(
        string='Kilos',
        digits=(16, 2),
        default=0.0,
    )
    precio_kilogrado = fields.Float(
        string='€/Kilogrado',
        digits='Precio Kilogrado',  # Usa la precisión decimal de 5 decimales
        default=0.0,
    )
    kilogrados = fields.Float(
        string='Kilogrados',
        digits='Kilogrados',  # Usa la precisión decimal de 0 decimales
        default=0.0,
    )

    @api.onchange('kilos', 'grado')
    def _onchange_kilos_grado_uva(self):
        """Recalcula kilogrados y el importe al cambiar kilos o grado."""
        self.kilogrados = self.kilos * self.grado
        # Actualiza también el importe (price_unit) ya que kilogrados cambió
        self.price_unit = self.precio_kilogrado * self.kilogrados

    @api.onchange('precio_kilogrado', 'kilogrados')
    def _onchange_importe_uva(self):
        """Recalcula el importe (price_unit) al cambiar €/kilogrado o kilogrados.
        Fórmula: Importe = €/kilogrado × Kilogrados
        """
        self.price_unit = self.precio_kilogrado * self.kilogrados

