# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMoveLine(models.Model):
    """
    Extiende stock.move.line para añadir:
      - signed_qty  : cantidad con signo (+entrada / -salida respecto al almacén)
      - running_bal : saldo acumulado calculado en el servidor (solo lectura)
    """
    _inherit = 'stock.move.line'

    signed_qty = fields.Float(
        string='Cantidad neta',
        compute='_compute_signed_qty',
        digits='Product Unit of Measure',
        store=True,
        help='Cantidad con signo: positiva si el producto entra en una ubicación '
             'interna (almacén), negativa si sale de ella.',
    )

    # ------------------------------------------------------------------ #
    #  Cálculo de signed_qty                                               #
    # ------------------------------------------------------------------ #
    @api.depends('quantity', 'location_id', 'location_dest_id', 'state')
    def _compute_signed_qty(self):
        """
        Lógica de signo:
          - Si el destino es interno  y el origen NO lo es  →  entrada  (+)
          - Si el origen  es interno  y el destino NO lo es →  salida   (-)
          - Movimientos internos (ambos internos) o externos (ninguno)   →  0
        En Odoo 18, qty_done y reserved_qty se unifican en el campo `quantity`.
        """
        internal = 'internal'
        for line in self:
            src_internal = (line.location_id.usage == internal)
            dst_internal = (line.location_dest_id.usage == internal)

            qty = line.quantity

            if dst_internal and not src_internal:
                line.signed_qty = qty          # entrada al almacén
            elif src_internal and not dst_internal:
                line.signed_qty = -qty         # salida del almacén
            else:
                line.signed_qty = 0.0          # traslado interno o externo puro
