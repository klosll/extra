# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# KLO
{
    'name': 'KLO - Invoice report no payment communication on footer',
    'version': '18.0.0.1.0',
    'summary': 'Invoice report without payment communication on footer by default',
    'description': 'No se imprime en el pie de la factura la comunicación de pago.',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account',],
    'data': [
        "reports/report_invoice.xml",
    ],
    "installable": True,
    "auto_install": False,
}
