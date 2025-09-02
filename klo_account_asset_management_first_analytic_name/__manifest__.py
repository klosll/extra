# Copyright 2009-2019 Noviat
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - João Marques
# Copyright 2025 KLO Ingeniería Informática S.L.L. - Manuel Calomarde Gómez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "KLO Assets Management analytic, first analytic name column",
    "version": "16.0.0.0.0",
    "license": "AGPL-3",
    "depends": ["account", "l10n_es_account_asset"],
    "external_dependencies": {"python": ["python-dateutil"]},
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "category": "Accounting & Finance",
    "data": [
        "views/account_asset.xml",
    ],
}
