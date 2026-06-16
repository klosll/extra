# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        """Propagar el partner del pedido de compra al movimiento de stock.

        En pedidos de compra con cantidades negativas, Odoo convierte el
        movimiento en una devolución durante _action_confirm():
          1. Intercambia location_id / location_dest_id.
          2. Cambia picking_type_id al tipo de retorno (p.ej. 'Órdenes de entrega').
          3. Llama _assign_picking() que crea un NUEVO albarán mediante
             _get_new_picking_values(), el cual toma el partner_id del campo
             stock.move.partner_id.

        El campo stock.move.partner_id se establece en _prepare_stock_move_vals
        con order_id.dest_address_id (solo relleno en envíos directos /
        dropship). Para pedidos normales queda vacío, y el nuevo albarán de
        devolución se crea sin proveedor asignado.

        Esta extensión rellena move.partner_id con el proveedor del pedido de
        compra cuando dest_address_id no está definido, de forma que el albarán
        de devolución resultante hereda correctamente la Dirección de entrega.
        No afecta al flujo de recepciones con cantidades positivas (el albarán
        inicial se crea con partner_id vía _prepare_picking() y no pasa por
        _get_new_picking_values()).
        """
        vals = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        # Solo rellenar cuando no hay dest_address_id (no es dropship)
        if not vals.get("partner_id") and self.order_id.partner_id:
            vals["partner_id"] = self.order_id.partner_id.id
        return vals

