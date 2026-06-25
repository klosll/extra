# -*- coding: utf-8 -*-
{
    'name': 'Historial de movimientos con cantidad con signo',
    'version': '18.0.1.0.0',
    'summary': 'Añade cantidad con signo y saldo acumulado al historial de movimientos de stock',
    'description': '''
        Añade dos columnas al historial de movimientos de productos
        (Inventario → Informes → Historial de movimientos):

        - **Cantidad neta**: positiva si el producto entra al almacén,
          negativa si sale. Se totaliza al pie de la lista.
        - **Saldo acumulado**: stock acumulado línea a línea
          (solo visible al filtrar por un único producto, ordenando por fecha).
    ''',
    'author': 'Personalizado',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
