# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Invoice Report Price Unit Untaxed',
    'summary': 'Muestra el precio unitario sin impuestos en el informe de factura',
    'description': """
        Invoice Report Price Unit Untaxed
        =================================
        Adapta el QWeb del informe de factura
        (account.report_invoice_document) para mostrar el precio unitario
        sin impuestos en la columna "Unit Price" de las líneas.

        El cálculo se realiza mediante el método compute_all de account.tax,
        extrayendo el valor total_excluded a partir del price_unit de cada
        línea, independientemente de si los impuestos están configurados
        como precio incluido o excluido.
    """,
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'version': '18.0.2.0.0',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'data': [
        'report/account_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
