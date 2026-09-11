# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "KLO HR Holidays Public (overtime)",
    "summary": "Soporte de festivos en el cálculo de horas extra (módulo propio KLO)",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "license": "AGPL-3",
    "description": """
Por qué se crea este módulo
===========================

En Odoo 15 KLO usaba el módulo OCA ``hr_holidays_public_overtime``, que
activaba el flag ``exclude_public_holidays=True`` durante el cálculo de horas
extra para que los festivos se excluyeran de dicho cálculo.

En Odoo 18 ese módulo OCA fue retirado y su lógica se integró parcialmente en
``hr_holidays_public`` (que ahora excluye festivos en las ausencias y en los
intervalos del calendario de recursos, vía el nuevo módulo
``calendar_public_holiday``), pero el override concreto de
``hr.attendance._update_overtime`` que activaba el flag durante el cálculo de
horas extra ya no existe en ningún módulo de Odoo 18.

Qué soluciona
=============

Este módulo propio de KLO restablece ese comportamiento: sobrescribe
``hr.attendance._update_overtime`` para marcar en el contexto
``exclude_public_holidays=True`` y ``employee_id``, de modo que el cálculo de
horas extra (que pasa por ``resource.calendar``) vuelve a excluir los festivos
del empleado, igual que hacía ``hr_holidays_public_overtime`` en v15.
""",
    "depends": [
        "hr_holidays_public",
        "hr_attendance",
    ],
    "auto_install": True,
    "installable": True,
}
