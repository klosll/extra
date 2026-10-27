# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Timesheet Partner & Project Filter",
    "version": "18.0.1.0.0",
    "summary": "Cliente en partes de horas (empresas primero) y filtrado de proyectos no finalizados",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Human Resources",
    "depends": [
        "hr_timesheet",
        "hr_timesheet_begin_end",
        "project_status",
        "sale_timesheet",
    ],
    "data": [
        "views/hr_analytic_timesheet.xml",
    ],
    "installable": True,
    "auto_install": False,
}
