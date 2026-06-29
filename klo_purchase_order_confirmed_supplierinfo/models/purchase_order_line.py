# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # Al crear líneas en pedidos ya confirmados, añadir el proveedor a la
        # ficha del producto igual que hace button_confirm en pedidos en borrador.
        confirmed_lines = res.filtered(
            lambda l: not l.display_type
            and l.product_id
            and l.order_id.state in ["purchase", "done"]
        )
        for line in confirmed_lines:
            line._add_supplier_to_product()
        return res

    def _add_supplier_to_product(self):
        """Añade el proveedor a la ficha del producto para esta línea si aún no
        está registrado, replicando la lógica de purchase.order._add_supplier_to_product()
        que se ejecuta durante button_confirm."""
        self.ensure_one()
        if self.display_type or not self.product_id:
            return
        order = self.order_id
        # Si el partner es una dirección de contacto, se usa la empresa padre
        partner = (
            order.partner_id
            if not order.partner_id.parent_id
            else order.partner_id.parent_id
        )
        already_seller = (
            partner | order.partner_id
        ) & self.product_id.seller_ids.mapped("partner_id")
        if already_seller or len(self.product_id.seller_ids) > 10:
            return
        price = self.price_unit
        # Convertir el precio a la UoM de compra del producto si difiere
        if self.product_id.product_tmpl_id.uom_po_id != self.product_uom:
            default_uom = self.product_id.product_tmpl_id.uom_po_id
            price = self.product_uom._compute_price(price, default_uom)
        supplierinfo = order._prepare_supplier_info(partner, self, price, self.currency_id)
        # Si existe un seller coincidente, conservar su nombre y código de producto
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=order.date_order and order.date_order.date(),
            uom_id=self.product_uom,
        )
        if seller:
            supplierinfo["product_name"] = seller.product_name
            supplierinfo["product_code"] = seller.product_code
        self.product_id.product_tmpl_id.sudo().write(
            {"seller_ids": [(0, 0, supplierinfo)]}
        )
