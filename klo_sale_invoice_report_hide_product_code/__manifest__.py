# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Sale/Invoice report hide product code',
    'version': '18.0.1.0.0',
    'summary': 'Hide the product code between brackets in sale order and invoice report lines',
    'description': 'Imprime las líneas de presupuesto/pedido y factura sin la referencia '
                   'entre corchetes "[CODIGO] " al inicio de la descripción.',
    'category': 'Sales/Sales',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['sale', 'account'],
    'data': [
        "reports/report_saleorder_document.xml",
        "reports/report_invoice_document.xml",
    ],
    "installable": True,
    "auto_install": False,
}