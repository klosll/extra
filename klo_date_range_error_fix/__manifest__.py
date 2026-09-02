# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "KLO - Corrección error zona horaria date_range",
    "summary": (
        "Módulo obsoleto en v18. En v15 corregía un bug de zona horaria del OCA "
        "date_range (uso de moment() local en _setDefaultValue). En v18 el OCA "
        "date_range fue reescrito con TreeEditor/DomainSelector y luxon, por lo "
        "que el bug ya no existe. Se conserva como dependencia vacía para no "
        "romper módulos que lo referencien."
    ),
    "version": "18.0.1.0.0",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "category": "Technical",
    "license": "AGPL-3",
    "depends": ["date_range"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
