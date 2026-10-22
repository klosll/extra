# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Sale Order Price Unit Untaxed',
    'summary': 'Muestra el precio unitario sin IVA en el informe de presupuesto/pedido de venta',
    'description': """
        Sale Order Price Unit Untaxed
        ==============================
        Adapta el QWeb del informe de presupuesto/pedido de venta
        (sale.report_saleorder_document) para mostrar el precio unitario
        sin impuestos en la columna "Precio unitario" de las líneas.

        El cálculo se realiza mediante el método compute_all de account.tax,
        extrayendo el valor total_excluded a partir del price_unit de cada
        línea, independientemente de si los impuestos están configurados
        como precio incluido o excluido.
    """,
    'author': 'KLO',
    'version': '18.0.2.0.1',
    'category': 'Sales/Sales',
    'depends': ['sale', 'portal'],
    'data': [
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
