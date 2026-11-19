# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Compra: cabecera con fuente pequeña',
    'version': '18.0.0.1.0',
    'summary': 'Fuente pequeña configurable para la cabecera de los informes de compra',
    'description': 'Crea el parámetro de sistema klo.report_layout_small_font_header_purchase '
                   'y aplica ese tamaño de fuente a la cabecera de los informes de Pedido de '
                   'compra y Solicitud de presupuesto, de forma independiente al de venta.',
    'category': 'Purchase',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['purchase'],
    'data': [
        "data/ir_config_parameter_data.xml",
        "views/report_assets.xml",
    ],
    "installable": True,
    "auto_install": False,
}
