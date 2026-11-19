# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Purchase RFQ hide expected date column',
    'version': '18.0.0.1.0',
    'summary': 'Hide the expected date column on the RFQ report',
    'description': 'Oculta la columna "Fecha prevista" (Expected Date) del informe de '
                   'Solicitud de presupuesto.',
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
