# -*- coding: utf-8 -*-
{
    'name': 'KLO Stock Picking Sale Type',
    'version': '14.0.1.0.0',
    'category': 'Warehouse,Stock',
    'summary': 'Add sale type column to stock picking tree view',
    'description': """
        This module adds a new column in the stock picking tree view to display
        the sale type of the partner address (partner_id.sale_type).
        The field is stored and allows filtering and grouping.
    """,
    'author': 'Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'sale',
        'sale_order_type',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}


