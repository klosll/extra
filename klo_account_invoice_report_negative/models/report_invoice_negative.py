# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import api, models
from odoo.tools.misc import format_amount

_logger = logging.getLogger(__name__)


class ReportInvoiceNegative(models.AbstractModel):
    """KLO. Modelo de reporte para factura rectificativa con importes en negativo.

    Hereda de report.account.report_invoice para reutilizar la lógica de QR codes
    y la estructura base. Añade al contexto de la plantilla:

    - fmt_amount: función helper para formatear importes negativos directamente
      en la plantilla QWeb (líneas y totales del pie).
    """

    _name = "report.klo_account_invoice_report_negative.report_invoice_negative"
    _description = "KLO Informe Factura Rectificativa Negativa"
    _inherit = "report.account.report_invoice"
    # KLO. El nombre del modelo genera una tabla >63 chars (límite PostgreSQL).
    # AbstractModel no crea tabla real, pero Odoo valida igualmente el nombre.
    _table = "report_klo_inv_negative"

    @api.model
    def _get_report_values(self, docids, data=None):
        """KLO. Extiende _get_report_values para pasar fmt_amount a la plantilla.

        fmt_amount se usa tanto en las líneas (price_subtotal/price_total en negativo)
        como en los totales del pie (document_tax_totals inline con valores negados).

        Uso en template: t-esc="fmt_amount(-line.price_subtotal, o.currency_id)"
        """
        rslt = super()._get_report_values(docids, data)

        # KLO. Helper para formatear importes negativos de líneas y pie de factura.
        def fmt_amount(amount, currency):
            return format_amount(self.env, amount, currency)

        rslt["fmt_amount"] = fmt_amount
        return rslt

