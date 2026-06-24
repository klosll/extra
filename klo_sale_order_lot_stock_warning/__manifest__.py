# -*- coding: utf-8 -*-
{
    'name': 'KLO Ventas - Aviso de stock insuficiente por lote',
    'version': '14.0.1.0.0',
    'summary': 'Avisa cuando el stock del lote asignado en la línea de pedido es insuficiente',
    'description': """
        Al asignar un lote (lot_id) o modificar la cantidad (product_uom_qty) en una
        línea de pedido de venta, comprueba el stock disponible de ese lote en la
        ubicación de origen del tipo de pedido
        (type_id.picking_type_id.default_location_src_id).

        Si la cantidad en stock es menor que la solicitada, muestra un mensaje
        informativo. El flujo normal de ejecución continúa en cualquier caso.
    """,
    'author': 'KLO',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': [
        'sale_order_lot_selection',
        'sale_order_type_picking',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
