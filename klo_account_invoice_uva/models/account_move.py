# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo relacionado para que el cliente JavaScript pueda saber si una
    # factura pertenece a un diario de uva sin hacer una llamada extra al servidor.
    # Se almacena en BD (store=True) para poder usarlo en vistas de lista.
    es_para_uva = fields.Boolean(
        string='Es factura de uva',
        related='journal_id.es_para_uva',
        store=True,
        readonly=True,
    )

    def get_formview_id(self, access_uid=None):
        """Devuelve el ID de la vista de formulario a usar al abrir/editar la factura.
        Si el diario tiene 'Es para uva' marcado, se usa la vista especializada
        view_move_form_uva en lugar de la vista estándar de facturas.
        """
        self.ensure_one()
        if self.journal_id.es_para_uva:
            return self.env.ref(
                'klo_account_invoice_uva.view_move_form_uva'
            ).id
        return super().get_formview_id(access_uid=access_uid)

    def _get_name_invoice_report(self):
        """Sobreescribe la selección del template de impresión de factura.
        Si la factura pertenece a un diario marcado como 'Es para uva',
        se usa el template especializado para uva en lugar del estándar.
        """
        self.ensure_one()
        if self.journal_id.es_para_uva:
            return 'klo_account_invoice_uva.klo_report_invoice_document_uva'
        return super()._get_name_invoice_report()

    @api.model
    def get_uva_formview_id_for_new(self):
        """Comprueba si el diario que se usará al crear el nuevo apunte tiene es_para_uva.
        Devuelve el ID de view_move_form_uva si corresponde, False en caso contrario.
        Llamado desde el cliente JavaScript en el momento de crear un nuevo registro,
        antes de que Odoo abra el formulario estándar.

        Lógica de resolución del diario (misma prioridad que Odoo):
          1. default_journal_id en el contexto → verificación directa.
          2. Sin diario explícito → se busca el primer diario del tipo que corresponda
             a default_move_type (sale para facturas cliente, purchase para proveedor).
        """
        # 1. Diario explícito en el contexto
        journal_id = self._context.get('default_journal_id')
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            if journal.es_para_uva:
                return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
            return False

        # 2. Resolver el diario predeterminado a partir del tipo de movimiento
        move_type = self._context.get('default_move_type', 'entry')
        if move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            journal_types = ['sale']
        elif move_type in ('in_invoice', 'in_refund', 'in_receipt'):
            journal_types = ['purchase']
        else:
            # Tipo de movimiento que no corresponde a facturas de uva
            return False

        company_id = self.env.company.id
        # Mismo orden de búsqueda que usa _search_default_journal en Odoo
        journal = self.env['account.journal'].search(
            [('company_id', '=', company_id), ('type', 'in', journal_types)],
            limit=1,
        )
        if journal and journal.es_para_uva:
            return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
        return False

