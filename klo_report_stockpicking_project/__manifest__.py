# -*- coding: utf-8 -*-
{
    'name': 'KLO - Proyecto en albarán de entrega',
    'summary': 'Muestra el campo Proyecto (project_id) en la cabecera del documento QWeb de entrega a cliente',
    'version': '18.0.1.0.0',
    'category': 'Stock/Reporting',
    'author': 'KLO',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'project',
    ],
    'data': [
        'report/report_deliveryslip_project.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

