# Copyright 2024 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Invoice number editable",
    "version": "16.0.0.1.0",
    "category": "Account",
    "sequence": 80,
    "summary": "Invoice number editable",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "installable": True,
    "auto_install": False,
    "depends": ["account", "account_invoice_fixed_discount", "account_banking_mandate"],
    "data": [
        "views/account_move_view.xml",
    ],
}
