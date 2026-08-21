# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Stock Picking report small font body',
    'version': '18.0.0.1.0',
    'summary': 'Stock Picking report body with smaller font size for more compact printing',
    'description': 'Se auto-crea el Parámetro de sistema: klo.stockpicking_report_body_small_font con valor 10 por defecto',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['sale',],
    'data': [
        'data/ir_config_parameter_data.xml',
        "data/report_paperformat_data.xml",
        "reports/report_deliveryslip.xml",
    ],
    "installable": True,
    "auto_install" : False,
}

