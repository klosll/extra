# -*- coding: utf-8 -*-
{
    'name': 'KLO Wizard Lot Reception',
    'version': '14.0.2.0.0',
    'category': 'Inventory',
    'summary': 'Wizard para capturar lotes en recepciones de compra',
    'description': """
Wizard para capturar lotes en recepciones de compra.
Permite registrar líneas de lotes y excedentes que quedan asociadas al albarán.
    """,
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'purchase',
        'sale_order_line_containers',
        'purchase_sale_reader',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'wizard/lot_reception_wizard_line_views.xml',
        'wizard/lot_reception_wizard_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
