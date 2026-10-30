# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Stock Picking Report Price Unit Untaxed',
    'version': '18.0.1.0.0',
    'summary': 'Muestra el precio unitario sin impuestos en el informe de albarán de entrega',
    'description': """
        Muestra el precio unitario sin impuestos en el informe de albarán de entrega.

        El módulo depende de stock_picking_report_valued (OCA), que añade las
        columnas de valoración al albarán, y de klo_sale_order_price_unit_untaxed,
        que aporta el campo price_unit_untaxed en la línea de pedido de venta.

        Sustituye el valor mostrado en la columna "Unit Price" por el precio
        unitario sin impuestos, conservando el formato del campo price_unit del
        formulario (mismos decimales, sin símbolo de moneda).
    """,
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'depends': [
        'stock_picking_report_valued',
        'klo_sale_order_price_unit_untaxed',
    ],
    'data': [
        'report/stock_picking_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
