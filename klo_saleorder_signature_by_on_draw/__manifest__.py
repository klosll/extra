# -*- coding: utf-8 -*-
{
    'name': 'KLO Sale Order - Firma del Cliente con signature',
    'version': '18.0.1.0.0',
    'summary': 'Permite dibujar la firma del cliente (signature) en la página Customer Signature del pedido de venta',
    'description': """
        En la página "Customer Signature" del formulario de Pedido de venta,
        usa el campo signature nativo de Odoo 18 con widget signature (firma dibujable).
        Permite al cliente dibujar su firma directamente en el formulario.
    """,
    'author': 'KLO',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

