# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import json

from odoo import models


class AccountStatementImport(models.TransientModel):
    _inherit = 'account.statement.import'

    def _parse_single_file_n43(self, n43):
        """Genera unique_import_id determinista por transacción Norma 43."""
        result = super()._parse_single_file_n43(n43)
        # result = (currency, account_number, [vals_bank_statement, ...])
        for vals_bank_statement in result[2]:
            seen = {}
            for line_vals in vals_bank_statement.get('transactions', []):
                n43_line = line_vals.get('n43_line')
                if not n43_line or line_vals.get('unique_import_id'):
                    continue
                base = self._klo_n43_unique_import_id(n43_line)
                seen[base] = seen.get(base, 0) + 1
                uid = base if seen[base] == 1 else '%s-%s' % (base, seen[base])
                line_vals['unique_import_id'] = uid
        return result

    def _klo_n43_unique_import_id(self, n43_line):
        """Hash estable de los campos identificativos del registro 22."""
        payload = '|'.join([
            str(n43_line.get('fecha_valor')),
            str(n43_line.get('fecha_oper')),
            '{:.2f}'.format(float(n43_line.get('importe', 0.0))),
            str(n43_line.get('num_documento', '')),
            str(n43_line.get('referencia1', '')),
            str(n43_line.get('referencia2', '')),
            str(n43_line.get('of_origen', '')),
            json.dumps(n43_line.get('conceptos', {}), sort_keys=True, ensure_ascii=False),
        ])
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:32]
