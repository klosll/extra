# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Invoice report no origin source on header',
    'version': '18.0.0.1.0',
    'summary': 'Invoice report without origin source on header by default',
    'description': 'No se imprime en la cabecera de la factura la lista del origen de los pedidos que se han facturado.',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account',],
    'data': [
        "reports/report_invoice.xml",
    ],
    "installable": True,
    "auto_install" : False,
}

