# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "KLO Fix Resource Calendar Std",
    "summary": (
        "Herramienta de corrección para el error de calendario "
        "resource_calendar_std faltante (ir.model.data)."
    ),
    "version": "18.0.1.0.0",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "category": "Technical",
    "license": "AGPL-3",
    "depends": ["resource"],
    "data": [
        "views/klo_resource_calendar_fix_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
