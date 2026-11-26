# -*- coding: utf-8 -*-
{
    'name': 'KLO Stock Picking Filter Lot No Company',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Permite seleccionar lotes sin compañía en albaranes y mermas',
    'description': """
Adaptación de stock_picking_filter_lot para clientes con productos compartidos
entre compañías (HT02695).

En v18 stock.lot ignora default_company_id al crear y calcula la compañía a
partir del producto, por lo que los lotes de productos sin compañía quedan sin
compañía asignada. Los dominios de stock_picking_filter_lot filtran los lotes
con "company_id = compañía del albarán", lo que oculta esos lotes al asignar
lotes en albaranes o mermas.

Este módulo sobreescribe esos dominios para aceptar también lotes sin compañía,
siguiendo el patrón que usa el propio core de stock (_get_next_serial). El
resto del filtrado del módulo original (producto y ubicación con stock) se
mantiene intacto.
    """,
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock_picking_filter_lot',
    ],
    'data': [
        'views/stock_move_line_view.xml',
        'views/stock_scrap_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
