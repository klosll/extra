# Copyright 2026 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class FacturaMatricialReport(models.AbstractModel):
    """KLO. Reporte de factura para impresora matricial (papel continuo).

    Hereda de report.account.report_invoice para reutilizar el contexto de
    datos del reporte estándar de facturas (doc_ids, doc_model, docs,
    qr_code_urls) sin añadir lógica propia.
    """

    _name = "report.klo_factura_matricial.report_factura_matricial"
    _description = "KLO Factura Matricial (papel continuo)"
    _inherit = "report.account.report_invoice"
