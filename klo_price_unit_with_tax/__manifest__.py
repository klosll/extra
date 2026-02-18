# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'KLO - Price Unit with Tax in Sale Order Lines',
    'version': '18.0.1.0.0',
    'summary': 'Add price unit with tax field in sale order lines',
    'description': """
        This module adds a new field 'price_unit_with_tax' to sale.order.line 
        that displays the unit price with taxes included. 
        This field is shown next to the standard price_unit field.
    """,
    'category': 'Sales/Sales',
    'author': 'KLO Ingeniería Informática S.L.L.',
    'website': 'https://www.klo.es',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

