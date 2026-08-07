# -*- coding: utf-8 -*-
{
    'name': 'KLO Wizard Lot Reception',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Wizard para capturar lotes en recepciones de compra',
    'description': """
Wizard para capturar lotes en recepciones de compra.
Permite crear líneas temporales con lotes y excedentes.
    """,
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'purchase',
        'sale_order_line_containers',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/lot_reception_wizard_line_views.xml',
        'wizard/lot_reception_wizard_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
