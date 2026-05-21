from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # KLO. Campo calculado que indica si se ha generado al menos un archivo Facturae.
    # En Odoo 15 (OCA l10n_es_facturae) los ficheros Facturae se almacenan en el
    # One2many l10n_es_facturae_attachment_ids (modelo account.move.facturae),
    # a diferencia de Odoo 18 donde existe el campo binario
    # l10n_es_edi_facturae_xml_file del módulo oficial l10n_es_edi_facturae.
    is_facturae_generated = fields.Boolean(
        string="Facturae generada",
        compute="_compute_is_facturae_generated",
        store=True,
        copy=False,
    )

    @api.depends("l10n_es_facturae_attachment_ids")
    def _compute_is_facturae_generated(self):
        for move in self:
            move.is_facturae_generated = bool(move.l10n_es_facturae_attachment_ids)

