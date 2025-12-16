# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Invoice report small font',
    'version': '18.0.0.1',
    'summary': 'Invoice report with smaller font size for more compact printing',
    'description': 'Se auto-crea el Parámetro de sistema: klo.invoice_report_small_font con valor 8 por defecto',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account',],
    'data': [
        'data/ir_config_parameter_data.xml',
        "data/report_paperformat_data.xml",
        "reports/report_invoice.xml",
    ],
    "installable": True,
    "application" : False,
}

