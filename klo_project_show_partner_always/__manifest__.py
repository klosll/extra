# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - Mostrar siempre el cliente en proyectos",
    "version": "18.0.1.0.0",
    "summary": "Muestra el campo Cliente (partner_id) en el formulario y la lista de proyectos aunque el proyecto no sea facturable (allow_billable=False)",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "category": "Project",
    "depends": ["sale_project"],
    "data": ["views/project_project_views.xml"],
    "installable": True,
    "auto_install": False,
}
