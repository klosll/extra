# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'KLO - Sale order report no taxes column',
    'version': '18.0.0.1.0',
    'summary': 'Sale order report without taxes column by default',
    'description': 'No se imprime en el pedido de venta la columna de impuestos por defecto.',
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

