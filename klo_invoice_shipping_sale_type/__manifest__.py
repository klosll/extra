# -*- coding: utf-8 -*-
{
    'name': 'KLO Invoice Shipping Sale Type',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Add shipping sale type column to invoice tree view',
    'description': """
        This module adds a new column in the invoice tree view to display
        the sale type of the shipping address (partner_shipping_id.sale_type).
        The field is stored and allows filtering and grouping.
    """,
    'author': 'Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.',
    'website': 'https://www.klo.es',
    'depends': [
        'account',
        'sale',
        'sale_order_type',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}


