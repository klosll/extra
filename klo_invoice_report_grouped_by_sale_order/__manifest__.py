# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Invoice Report Grouped by Sale Order",
    "version": "18.0.1.0.1",
    "summary": "Imprime facturas con líneas agrupadas por pedido de venta con fecha de entrega ordenados de fecha reciente a antigua",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Accounting & Finance",
    "depends": ["account", "sale"],
    "data": ["views/report_invoice.xml"],
    "installable": True,
    "auto_install": False,
}
