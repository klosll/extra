# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'KLO - Bank Statement Cascade Delete',
    'version': '18.0.1.0.0',
    'summary': 'Elimina apuntes contables al borrar extracto bancario',
    'description': """
Al eliminar un extracto bancario (account.bank.statement), se eliminan también
las líneas del extracto (account.bank.statement.line) y sus correspondientes
apuntes contables (account.move.line).

Esto corrige el comportamiento de Odoo 18 donde al eliminar un extracto bancario
las líneas quedaban huérfanas y los apuntes contables permanecían visibles en
Facturación → Contabilidad → Apuntes contables.
    """,
    'category': 'Accounting/Accounting',
    'license': 'AGPL-3',
    'author': 'KLO Ingenieria Informatica S.L.L.',
    'website': 'https://www.klo.es',
    'depends': ['account'],
    'data': [],
    'installable': True,
    'auto_install': False,
}
