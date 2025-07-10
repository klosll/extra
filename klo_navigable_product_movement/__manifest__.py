# Copyright 2024 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Navigable Product Movement",
    "version": "15.0.0.1.0",
    "category": "Inventory",
    "sequence": 80,
    "summary": "Do navigable Product Movement from Product form",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "installable": True,
    "auto_install": False,
    "depends": [
        "stock",
        "sale_stock",
        "purchase_stock",
    ],
    "data": [
        "views/stock_move_line_views.xml",
    ],
}
