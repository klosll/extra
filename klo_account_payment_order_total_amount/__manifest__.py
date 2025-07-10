# © 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "KLO Account Payment Order Total Amount",
    "version": "15.0.2.7.2",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L., "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/bank-payment",
    "development_status": "Mature",
    "category": "Banking addons",
    "external_dependencies": {"python": ["lxml"]},
    "depends": ["account_payment_order"],
    "data": [
        "views/account_payment_line.xml",
    ],
    "installable": True,
}
