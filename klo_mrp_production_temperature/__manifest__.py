# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "KLO MRP Production Temperature",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "KLO",
    "website": "",
    "depends": [
        "mrp",
        "custom_mrp_line_cost",
    ],
    "data": [
        "views/mrp_production_views.xml",
        "views/stock_move_line_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
