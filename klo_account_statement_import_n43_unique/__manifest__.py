# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'KLO - Norma 43 Unique Import ID',
    'version': '18.0.1.0.0',
    'summary': 'Genera unique_import_id en la importación Norma 43 para evitar duplicados',
    'description': """
Al importar extractos bancarios españoles en formato Norma 43 (módulo
l10n_es_account_statement_import_n43), el parser no genera el campo
unique_import_id, por lo que reimportar el mismo fichero crea apuntes duplicados.

Este módulo genera un unique_import_id determinista por transacción a partir de
los campos del registro 22 (fecha, importe, número de documento, referencias,
oficina y conceptos), permitiendo que el mecanismo anti-duplicados de Odoo
(restricción UNIQUE y filtro en _create_bank_statements) actúe correctamente.
    """,
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['l10n_es_account_statement_import_n43'],
    'data': [],
    'installable': True,
    'auto_install': False,
}
