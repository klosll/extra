# -*- coding: utf-8 -*-
{
    'name': 'KLO Sale Projects line price and discount inherit from xf_sale_project',
    'version': '15.0.0',
    'summary': """
    Project related sale quotations, sale orders and invoices,
    Project Sale Orders,
    Project Products,
    Project Sale Quotations,
    Project Invoices,
    Sale Order Project,
    Invoice Project,
    Product Project,
    """,
    'category': 'Project,Sales,Accounting',
    'author': 'KLO inherit from XFanis',
    'support': 'KLO Ingeniería Informática S.L.L.',
    'website': 'https://klo.es',
    'license': 'AGPL-3',
    'description':
        """
        KLO. Crear y relacionar pedido con proyecto.
        Este módulo hereda de xf_sale_project.
        Realiza el cálculo del precio unitario y descuento que tenga el artículo que se pone en la línea de poductos
        porque el módulo padre no asigna precio ni descuento en la línea.
        Lo hace teniendo en cuenta las condiciones asignadas a la tarifa del cliente.
        """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project.xml',
    ],
    'depends': ['xf_sale_project'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
