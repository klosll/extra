# Copyright 2023 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Price By Packaging",
    "version": "16.0.1.0.0",
    "category": "Account",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "depends": [
        "account",
        "account_invoice_qty_by_packaging",
    ],
    "excludes": [],
    "data": [
        "views/account_move_views.xml",
        "report/account_invoice_report.xml"
    ],
    "installable": True,
}
