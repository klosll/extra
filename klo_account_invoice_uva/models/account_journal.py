# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    es_para_uva = fields.Boolean(
        string='Es para uva',
        default=False,
        help='Si está marcado, al crear una nueva factura desde el dashboard '
             'se utilizará la vista especializada para facturas de uva.',
    )

    def action_create_new(self):
        """Sobrescribe la acción de creación de factura.
        Si el diario está marcado como 'Es para uva', abre la vista
        especializada view_move_form_uva en lugar de la estándar.
        """
        if self.es_para_uva:
            return {
                'name': _('Crear factura de uva'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': self.env.ref(
                    'klo_account_invoice_uva.view_move_form_uva'
                ).id,
                'context': self._get_move_action_context(),
            }
        return super().action_create_new()

