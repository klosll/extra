# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Informe de pedido de venta sin comercial en cabecera",
    "version": "18.0.1.0.0",
    "summary": "No imprime el comercial en la cabecera del informe de pedido de venta",
    "description": "No se imprime en la cabecera del pedido de venta el comercial por defecto.",
    "category": "Sales/Sales",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "depends": ["sale"],
    "data": ["reports/report_saleorder_document.xml"],
    "installable": True,
    "auto_install": False,
}