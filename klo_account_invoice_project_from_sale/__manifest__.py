# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "KLO Project on Invoice from Origin Sale Order and print on sale order and invoice reports",
    "version": "18.0.1.0.1",
    "author": "KLO Ingeniería Informática S.L.L.",
    "maintainers": ["Manuel Calomarde Gómez"],
    "category": "Accounting",
    "website": "https://hithub.com/klosll/extra",
    "license": "AGPL-3",
    "depends": ["account",
                'sale',
                'sale_project',
                'project',
                ],
    "data": ["views/account_move_view.xml",
             "reports/sale_order_templates.xml",
             "reports/invoice_report.xml",
             ],
    "installable": True,
    "auto_install": False,
}
