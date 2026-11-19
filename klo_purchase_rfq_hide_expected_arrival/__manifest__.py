# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Purchase RFQ hide expected arrival on header',
    'version': '18.0.0.1.0',
    'summary': 'Hide expected arrival on header while the document is still an RFQ',
    'description': 'Oculta la llegada esperada de la cabecera del informe de Pedido de '
                   'compra mientras el documento sigue siendo una Solicitud de '
                   'presupuesto (sin confirmar el pedido).',
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
