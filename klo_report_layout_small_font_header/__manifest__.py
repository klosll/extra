# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Report layout small font header',
    'version': '18.0.0.1.0',
    'summary': 'Report layout header with smaller font size for more compact printing',
    'description': 'Se auto-crea el Parámetro de sistema: klo.report_layout_small_font_header con valor 10 por defecto',
    'category': 'Accounting/Accounting',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account',],
    'data': [
        'data/ir_config_parameter_data.xml',
        "views/report_assets.xml",
    ],
    "installable": True,
    "auto_install" : False,
}

