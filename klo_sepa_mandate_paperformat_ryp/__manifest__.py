# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "KLO - SEPA Mandate paper format RYP",
    "version": "18.0.0.1.0",
    "summary": (
        "Mantiene el informe Mandato SEPA asociado al formato de papel "
        "'European A4 low margin for SEPA Ruiz y Pérez'"
    ),
    "description": """
Ajuste para RYP.

El módulo account_banking_sepa_direct_debit define la acción de informe
"Mandato SEPA" (account_banking_sepa_direct_debit.report_sepa_direct_debit_mandate)
en un fichero de datos sin noupdate, con paperformat_id fijado a su formato de papel
"European A4 low margin for SEPA". Por eso, cada actualización del módulo (-u) vuelve
a sobrescribir el campo y el informe pierde el formato de papel asignado manualmente.

Este módulo se carga después (depende de account_banking_sepa_direct_debit) y
reasigna en cada instalación/actualización el formato de papel
"European A4 low margin for SEPA Ruiz y Pérez" al informe Mandato SEPA, de modo que
la asignación sobrevive a los "-u all".
""",
    "category": "Accounting/Accounting",
    "license": "AGPL-3",
    "author": "KLO Ingenieria Informatica S.L.L.",
    "website": "https://www.klo.es",
    "depends": ["account_banking_sepa_direct_debit"],
    "data": [
        "data/report_sepa_direct_debit_mandate_data.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "auto_install": False,
}
