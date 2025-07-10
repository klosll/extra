# -*- coding: utf-8 -*-
{
    'name': 'Sale Projects',
    'version': '1.0.0',
    'summary': """
    Project related sale quotations, sale orders and invoices,
    Project Sale Orders,
    Project Products,
    Project Sale Quotations,
    Project Invoices,
    Sale Order Project,
    Invoice Project,
    Product Project,
    """,
    'category': 'Project,Sales,Accounting',
    'author': 'XFanis',
    'support': 'xfanis.dev@gmail.com',
    'website': 'https://xfanis.dev/odoo.html',
    'license': 'OPL-1',
    'price': 18,
    'currency': 'EUR',
    'description':
        """
        Sale Projects
        Project related sale quotations, sale orders and invoices
        The module helps link sale orders and invoices to projects.
        
        Key Features:
        - Using project products to create sale quotations more quickly
        - Linking sale order and invoices to projects
        - Ability to apply project details through sale order or invoice form
        - Multi-Company and Multi-Currency features of Odoo System are supported
        """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/res_config_settings.xml',
    ],
    'depends': ['project', 'sale_management'],
    'qweb': [],
    'images': [
        'static/description/xf_sale_project.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
