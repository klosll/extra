{
    'name': 'KLO - Estado Facturae en Facturas',
    'version': '18.0.1.0.0',
    'summary': 'Muestra si se ha generado el archivo Facturae en la lista de facturas',
    'description': """
        Añade un campo booleano calculado 'is_facturae_generated' en account.move
        que indica si se ha generado el archivo Facturae XML mediante la acción
        "Crear archivo de Facturae". También añade una columna opcional en la
        lista de facturas para visualizar este estado.
    """,
    'author': 'KLO',
    'category': 'Accounting',
    'depends': ['account', 'l10n_es_edi_facturae'],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

