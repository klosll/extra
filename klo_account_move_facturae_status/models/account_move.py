from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_facturae_generated = fields.Boolean(
        string='Facturae generada',
        compute='_compute_is_facturae_generated',
        store=True,
        copy=False,
    )

    @api.depends('l10n_es_edi_facturae_xml_file')
    def _compute_is_facturae_generated(self):
        for move in self:
            move.is_facturae_generated = bool(move.l10n_es_edi_facturae_xml_file)

