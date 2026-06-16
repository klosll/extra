# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _update_supplierinfo(self, seller):
        """Extiende el método del módulo OCA purchase_order_supplierinfo_update
        para actualizar también la fecha de la última compra (purchase_date)
        en la tarifa del proveedor.
        """
        super()._update_supplierinfo(seller)
        order_date = self.order_id.date_order
        new_date = order_date.date() if order_date else fields.Date.today()
        if seller.purchase_date != new_date:
            seller.sudo().purchase_date = new_date

