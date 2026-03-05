# -*- coding: utf-8 -*-
{
    'name': 'KLO - Apuntes Analíticos por Categoría de Contacto',
    'version': '15.0.1.0.0',
    'summary': 'Permite filtrar los Apuntes Analíticos por la Categoría del Contacto (partner_id)',
    'description': """
        Módulo que añade a account.analytic.line un campo relacionado con la categoría
        del contacto (res.partner.category) para poder filtrar y agrupar los apuntes
        analíticos por dicha categoría desde Contabilidad → Apuntes analíticos.
    """,
    'author': 'KLO',
    'category': 'Accounting/Accounting',
    'depends': ['analytic', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}

