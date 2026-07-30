# -*- coding: utf-8 -*-
{
    'name': 'KLO Sale Order - Firma del Cliente con customer_signature',
    'version': '14.0.1.0.0',
    'summary': 'Sustituye signature por customer_signature en la página Customer Signature del pedido de venta',
    'description': """
        En la página "Customer Signature" del formulario de Pedido de venta,
        reemplaza el campo signature por customer_signature (widget de firma dibujable).
        Permite al cliente dibujar su firma directamente en el formulario.
    """,
    'author': 'KLO',
    'category': 'Sales',
    'depends': ['sale', 'sale_order_digitized_signature'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

