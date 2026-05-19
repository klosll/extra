# -*- coding: utf-8 -*-
{
    'name': 'KLO Ventas - Precio ponderado unitario en pivot',
    'version': '14.0.1.0.0',
    'summary': 'Añade la medida "P. ponderado uni." al pivot de análisis de ventas',
    'description': """
        Añade una nueva medida calculada "P. ponderado uni." (precio_ponderado_unitario)
        al informe pivot de Ventas (sale.report).
        Se calcula como: Base imponible (price_subtotal) / Cantidad enviada (qty_delivered).
    """,
    'author': 'KLO',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

