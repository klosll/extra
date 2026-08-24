# -*- coding: utf-8 -*-
{
    'name': 'KLO Stock Lot Last Cost',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Precio de la última compra del producto en lote e informe de inventario',
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'account',
        'stock_production_lot_purchase_cost',
    ],
    'data': [
        'views/stock_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
