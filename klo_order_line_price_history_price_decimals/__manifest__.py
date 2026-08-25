# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Order Line Price History Price Decimals",
    "version": "18.0.1.0.0",
    "summary": "Muestra price_unit del historial de precios (ventas y compras) con la precisión Product Price",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Sales",
    "depends": [
        "sale_order_line_price_history",
        "purchase",
    ],
    "data": [
        "views/purchase_order_line_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
