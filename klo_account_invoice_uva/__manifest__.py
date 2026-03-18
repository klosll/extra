{
    'name': 'KLO - Facturas de Uva',
    'version': '16.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Gestión de facturas de uva con campos de grado, kilos y kilogrados',
    'description': """
        Módulo para gestionar facturas de compra/venta de uva.
        Añade campos específicos (grado, kilos, kilogrados, precio por kilogrado)
        en las líneas de factura y una vista especializada activada por diario.
    """,
    'author': 'Manuel Calomarde Gomez - KLO Ingenieria Informatica S.L.L.',
    'depends': ['account'],
    'data': [
        'views/account_journal_views.xml',
        'views/account_move_uva_views.xml',
        'report/report_invoice_uva.xml',
        'views/report_invoice_uva_wrappers.xml',
    ],
    'assets': {
        # Parche del ListController para redirigir a la vista especializada
        # cuando el diario de la factura tiene 'es_para_uva' = True
        'web.assets_backend': [
            'klo_account_invoice_uva/static/src/js/account_move_list_open.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
