# -*- coding: utf-8 -*-
{
    'name': 'Desbloquear Albarán',
    'version': '14.0.1.0.0',
    'summary': 'Acción de servidor para desbloquear albaranes desde la lista de traspasos',
    'description': """
Acción de servidor "Desbloquear albarán" que permite desbloquear
albaranes bloqueados directamente desde la vista de lista de traspasos.
    """,
    'category': 'Inventory/Inventory',
    'author': 'KLO',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
