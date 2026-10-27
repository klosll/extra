# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "KLO - Factura Matricial",
    "summary": (
        "Factura para impresora matricial en papel continuo 279x210 mm: imprime "
        "los datos en posiciones fijas (mm) sobre formulario preimpreso, "
        "reutilizando el contexto de account.report_invoice_document."
    ),
    "version": "18.0.1.0.1",
    "author": "KLO Ingeniería Informática S.L.L.",
    "license": "AGPL-3",
    "website": "https://www.klo.es",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "report/report_factura_matricial.xml",
        "views/report_action.xml",
    ],
    "installable": True,
    "auto_install": False,
}
