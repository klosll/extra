# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Sale order report no expiration date on header',
    'version': '18.0.0.1.0',
    'summary': 'Sale order report without expiration date on header by default',
    'description': 'No se imprime en la cabecera del pedido de venta la fecha de vencimiento por defecto.',
    'category': 'Sales/Sales',
    "license": "AGPL-3",
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['sale',],
    'data': [
        "reports/report_saleorder_document.xml",
    ],
    "installable": True,
    "auto_install" : False,
}

