# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Purchase hide buyer on header',
    'version': '18.0.0.1.0',
    'summary': 'Hide buyer on header',
    'description': 'Oculta el comprador de la cabecera del informe de Pedido de compra en todos los estados (Solicitud de presupuesto y Pedido confirmado).',
    'category': 'Purchase',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['purchase'],
    'data': [
        "reports/purchase_order_report.xml",
    ],
    "installable": True,
    "auto_install": False,
}
