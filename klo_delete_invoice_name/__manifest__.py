{
    'name': 'Delete invoice name in draft mode for delete invoice',
    'version': '14.0.0',
    'category': 'Accounting',
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'summary': 'Delete invoice name in draft mode. After delete invoice name, you can to delete this invoice.',
    'description': '''After delete invoice name in draft mode, you can to delete this invoice.''',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
    ],
    'images': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
