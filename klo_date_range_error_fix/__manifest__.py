# -*- coding: utf-8 -*-
{
    "name": "KLO - Corrección error zona horaria date_range",
    "summary": (
        "Corrige el bug de zona horaria en el módulo OCA date_range: "
        "_setDefaultValue usaba moment() (hora local) en lugar de moment.utc(), "
        "provocando que al seleccionar un rango de fechas aparecieran datos del día anterior."
    ),
    "version": "15.0.1.0.1",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "category": "Technical",
    "license": "AGPL-3",
    "depends": ["date_range"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            # KLO. Carga DESPUÉS de date_range (garantizado por dependencia de módulo)
            # para sobreescribir el método _setDefaultValue con la corrección UTC
            "klo_date_range_error_fix/static/src/js/klo_date_range_fix.esm.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}

