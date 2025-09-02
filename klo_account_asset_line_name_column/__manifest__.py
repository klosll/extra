# Copyright 2024 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Asset Line Name Column",
    "version": "16.0.0.1.0",
    "category": "Account",
    "sequence": 80,
    "summary": "Column Name of Asset",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "installable": True,
    "auto_install": False,
    "depends": ["account", "account_asset_line_menu", "klo_account_asset_management_analytic_percent_columns"],
    "data": [
        "views/account_asset_line_views.xml",
    ],
}
