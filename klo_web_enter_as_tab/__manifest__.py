# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Enter como Tab en listas editables",
    "version": "18.0.1.0.0",
    "summary": "Hace que la tecla Enter se comporte como Tab en las listas editables x2many",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Technical",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "klo_web_enter_as_tab/static/src/js/list_enter_as_tab.js",
        ],
    },
    "installable": True,
    "auto_install": False,
}