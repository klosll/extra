# -*- coding: utf-8 -*-
# KLO
{
    'name': 'KLO - Report layout footer inter line size',
    'version': '18.0.0.1',
    'summary': 'Report layout footer inter line size for more compact printing',
    'description': '''Se auto-crea el Parámetro de sistema: klo.report_layout_inter_line_footer con valor 1.0 por defecto
                    1.0 = sin espacio adicional entre líneas
                    1.2 = 20% de espacio adicional (recomendado)
                    1.5 = 50% de espacio adicional''',
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
    "application" : False,
}

