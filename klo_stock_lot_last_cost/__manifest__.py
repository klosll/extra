# -*- coding: utf-8 -*-
{
    'name': 'KLO Stock Lot Last Cost',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Precio del último pedido de compra del producto en lote e informe de inventario',
    'description': """
Este módulo añade el campo "Precio última compra" (purchase_last_cost) al lote
(stock.production.lot) y al informe de inventario, así como el campo
"Valor última compra" (purchase_last_value) en la vista de lista de stock a mano.

El precio que se muestra es el PRECIO UNITARIO de la línea del producto del
ÚLTIMO PEDIDO DE COMPRA realizado (purchase.order.line), y NO el de la factura
de compra. Se usa el pedido de compra en lugar de la factura porque el pedido
puede existir antes de que se genere la factura, y el objetivo de este dato es
valorar lo que se ha PEDIDO, no lo que se ha facturado.

Se consideran únicamente los pedidos confirmados o bloqueados (estados
'purchase' y 'done'); se excluyen los borradores, RFQ y pedidos cancelados.
    """,
    'author': 'KLO Ingeniería Informática',
    'website': 'https://www.klo.es',
    'depends': [
        'stock',
        'purchase',
        'stock_production_lot_purchase_cost',
    ],
    'data': [
        'views/stock_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
