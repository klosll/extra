# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Purchase hide secondary qty column',
    'version': '18.0.0.1.0',
    'summary': 'Hide the secondary qty (Second Qty) column on purchase reports',
    'description': 'Oculta la columna "Segunda Ctd" (Second Qty) de los informes de '
                   'Pedido de compra y de Solicitud de presupuesto.',
    'category': 'Purchase',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['purchase', 'purchase_order_secondary_unit'],
    'data': [
        "reports/purchase_order_report.xml",
    ],
    "installable": True,
    "auto_install": False,
}
