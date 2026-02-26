# Copyright 2026 Manuel Calomarde Gómez - KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Liquidation Stamp on Liquidation Invoice Report",
    'summary': """Añade la firma en Factura de liquidación. El sello se asigna en la Compañía.""",
    'version': '14.0.1.0.0',
    'description': """Añade la firma en Factura de liquidación. El sello se asigna en la Compañía.""",
    "category": "Generic Modules",
    "license": "AGPL-3",
    "author": "KLO Ingeniería Informática S.L.L.",
    "website": "https://www.klo.es",
    "depends": [
        "base",
        "batch_liquidation_report",
    ],
    "data": [
        "views/res_company_view.xml",
        "report/liquidation_account_move_report.xml",
    ],
    "installable": True,
}
