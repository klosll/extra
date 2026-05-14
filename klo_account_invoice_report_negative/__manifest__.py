# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "KLO Account Invoice Report Negative",
    "summary": (
        "Imprime facturas rectificativas a clientes con cantidades e importes en negativo. "
        "Solo visible en el menú Imprimir de facturas rectificativas (out_refund)."
    ),
    "version": "15.0.1.0.0",
    "author": "KLO Ingeniería Informática S.L.L.",
    "license": "AGPL-3",
    "website": "https://www.klo.es",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "report/report_invoice_negative.xml",
        "views/report_action.xml",
    ],
    "installable": True,
}

