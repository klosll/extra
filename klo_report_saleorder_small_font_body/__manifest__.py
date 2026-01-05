# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Sale Order report small font body',
    'version': '18.0.0.1',
    'summary': 'Sale Order report body with smaller font size for more compact printing',
    'description': 'Se auto-crea el Parámetro de sistema: klo.saleorder_report_body_small_font con valor 10 por defecto',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['sale',],
    'data': [
        'data/ir_config_parameter_data.xml',
        "data/report_paperformat_data.xml",
        "reports/sale_order_templates.xml",
    ],
    "installable": True,
    "application" : False,
}

