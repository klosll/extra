# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Lot expiry date on printed invoice',
    'version': '1.0',
    'category': 'Account',
    'license': 'LGPL-3',
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    'summary': 'Invoice Lot Expiry Date',
    'description': """
Expiry date on printed invoice
""",
    'depends': ['stock_account'],
    'data': [
        "report/report_invoice.xml",
    ],
    'installable': True,
    'auto_install': True,
}
