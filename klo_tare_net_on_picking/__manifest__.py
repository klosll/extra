# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Tare and net on purchase and sale picking",
    "version": "16.0.1.0.0",
    "category": "",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "maintainers": ["Manuel Calomarde Gómez"],
    "website": "https://www.klo.es",
    "depends": [
        "web",
        "sale",
        "purchase",
        "purchase_stock",
        "account_fiscal_year",
        "klo_pways_transportor_management",
    ],
    "data": [
        "data/report_paperformat_data.xml",
        "data/tare_net_gross_data.xml",
        "views/purchase_views.xml",
        "views/sale_order_views.xml",
        "views/res_company_views.xml",
        "report/report_template.xml",
        "report/purchase_reports.xml",
        "report/purchase_order_templates.xml",
        "report/sale_order_reports.xml",
        "report/sale_order_templates.xml",
    ],
    "installable": True,
    "application": False,
}
