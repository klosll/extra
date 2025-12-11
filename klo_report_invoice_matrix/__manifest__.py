# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Invoice dot matrix report',
    'version': '18.0.0.1',
    'summary': 'Invoice dot matrix report',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account',],
    'data': [
        "data/report_paperformat_data.xml",
        "reports/invoice_report_templates.xml",
        "reports/report_invoice.xml",
    ],
    "installable": True,
    "application" : False,
}

