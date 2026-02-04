# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2026 KLO Ingeniería Informática S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "KLO Sale Order Line Menu with Product Brand",
    "version": "18.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": "Adds a Sale Order Lines Menu and allows grouping by Product Brand",
    'description': 'Se amplia el módulo de OCA, sale_order_line_menu para que se pueda agrupar por Marca de Producto.',
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale","sale_order_line_menu"],
    "category": "Sales/Sales",
    "data": [
        "views/sale_order_line_views.xml",
    ],
    "installable": True,
    "maintainer": ["KLO Ingeniería Informática S.L."],
    "development_status": "Beta",
}
