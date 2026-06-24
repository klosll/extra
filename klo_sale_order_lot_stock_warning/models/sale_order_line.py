# -*- coding: utf-8 -*-
from odoo import _, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_lot_stock_qty(self, lot, location):
        """Devuelve la cantidad disponible del lote en la ubicación indicada."""
        quants = self.env["stock.quant"].search([
            ("product_id", "=", lot.product_id.id),
            ("lot_id", "=", lot.id),
            ("location_id", "=", location.id),
        ])
        return sum(quants.mapped("quantity"))

    def _check_lot_stock_warning(self):
        """
        Comprueba el stock del lote asignado frente a la cantidad pedida.
        Devuelve un dict de warning si hay stock insuficiente, o None en caso contrario.
        """
        for line in self:
            if not line.lot_id:
                continue
            pick_type = (
                line.order_id.type_id
                and line.order_id.type_id.picking_type_id
            )
            if not pick_type or not pick_type.default_location_src_id:
                continue
            location = pick_type.default_location_src_id
            stock_qty = line._get_lot_stock_qty(line.lot_id, location)
            if stock_qty < line.product_uom_qty:
                return {
                    "warning": {
                        "title": _("Stock insuficiente"),
                        "message": _(
                            "El lote '%s' del producto '%s' solo tiene %.2f %s "
                            "disponibles en la ubicación '%s', pero se han solicitado %.2f %s."
                        ) % (
                            line.lot_id.name,
                            line.product_id.display_name,
                            stock_qty,
                            line.product_uom.name,
                            location.complete_name,
                            line.product_uom_qty,
                            line.product_uom.name,
                        ),
                    }
                }
        return None

    @api.onchange("lot_id")
    def _onchange_lot_id_check_stock(self):
        return self._check_lot_stock_warning()

    @api.onchange("product_uom_qty")
    def _onchange_product_uom_qty_check_stock(self):
        return self._check_lot_stock_warning()
