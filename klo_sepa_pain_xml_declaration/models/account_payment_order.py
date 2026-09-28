# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    # Cabecera exigida por el banco: incluye standalone="no".
    # lxml genera por defecto <?xml version='1.0' encoding='UTF-8'?> sin
    # standalone y ningun modulo OCA lo contempla.
    _SEPA_XML_DECLARATION = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'

    def finalize_sepa_file_creation(self, xml_root, gen_args):
        xml_string, filename = super().finalize_sepa_file_creation(xml_root, gen_args)
        # Normalizar solo la declaracion XML (primera linea). La validacion
        # XSD ya se hizo en super() y la declaracion no afecta a la validez.
        xml_string = re.sub(
            br"^<\?xml[^?\n]*\?>",
            self._SEPA_XML_DECLARATION,
            xml_string,
            count=1,
        )
        return xml_string, filename
