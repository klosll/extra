# Copyright 2026 KLO
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):
        res = super().write(vals)
        # Además del trigger base (price_unit, discount), disparar también
        # si cambian los descuentos individuales del triple descuento
        triple_discount_fields = {"discount1", "discount2", "discount3"}
        if triple_discount_fields & set(vals.keys()):
            self.update_supplierinfo_price()
        return res

    def _update_supplierinfo(self, seller):
        """Extiende el método base para actualizar también discount1, discount2
        y discount3 en el product.supplierinfo correspondiente."""
        super()._update_supplierinfo(seller)
        # Actualizar los descuentos individuales del triple descuento
        updates = {}
        if self.discount1 != seller.discount1:
            updates["discount1"] = self.discount1
        if self.discount2 != seller.discount2:
            updates["discount2"] = self.discount2
        if self.discount3 != seller.discount3:
            updates["discount3"] = self.discount3
        if updates:
            seller.sudo().write(updates)

