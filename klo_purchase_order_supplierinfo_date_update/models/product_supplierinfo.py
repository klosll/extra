# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_date = fields.Date(
        string="F. última compra",
        readonly=True,
        copy=False,
        help="Fecha de la última compra confirmada de este producto al proveedor.",
    )

