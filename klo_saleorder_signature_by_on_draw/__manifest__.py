# -*- coding: utf-8 -*-
{
    'name': 'KLO Sale Order - Firma: signed_by y signed_on encima del widget de firma',
    'version': '14.0.1.0.0',
    'summary': 'Muestra signed_by y signed_on encima del campo customer_signature en el pedido de venta',
    'description': """
        Añade los campos signed_by y signed_on encima del campo customer_signature
        en el formulario de Pedido de venta (página Customer Signature),
        alineados a la izquierda.
        No se eliminan de su posición original.
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

