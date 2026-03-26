# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "KLO Purchase and Invoice final partner",
    "summary": "Add to purchases order and invoices the final partner."
               "When invoice is validated, partner set to analitics lines",
    "version": "15.0.1.1.0",
    "author": "KLO Ingeniería Informática S.L.L.",
    "license": "AGPL-3",
    "website": "https://www.klo.es",
    "category": "Purchase",
    "depends": [
        "purchase_stock",
        "account",
        "analytic",
        "account_analytic_distribution",
    ],
    "data": [
        "views/purchase_view.xml",
        "views/account_move_view.xml",
        "views/account_analytic_line_view.xml",
    ],
    "installable": True,
}


