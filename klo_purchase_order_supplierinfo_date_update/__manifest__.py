# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Fecha última compra en tarifa de proveedor",
    "version": "18.0.1.0.0",
    "summary": "Añade la fecha de la última compra en las tarifas de proveedor del producto",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Purchase",
    "depends": [
        "purchase_order_supplierinfo_update",
    ],
    "data": [
        "views/product_supplierinfo_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}

