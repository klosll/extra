{
    "name": "Resumen de IVA devengado y deducido",
    "summary": "Informe resumido de IVA devengado y deducido por tipo de IVA, "
    "cuadrado con las casillas del modelo 303",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "KLO",
    "license": "AGPL-3",
    "depends": ["account", "l10n_es", "l10n_es_aeat", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/vat_summary_views.xml",
        "report/vat_summary_xlsx.xml",
    ],
    "installable": True,
}
