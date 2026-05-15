# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Supplier Discounted Price",
    "version": "18.0.1.0.0",
    "summary": "Muestra el precio con los 3 descuentos aplicados en la tarifa de precios de proveedor",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "category": "Purchase",
    "depends": ["purchase_triple_discount"],
    "data": [
        "views/product_supplierinfo_view.xml",
    ],
    "installable": True,
}

