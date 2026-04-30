# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)

    def write(self, vals):
        """KLO. Proteger sale_partner_id en líneas contra sobreescritura al guardar.

        PROBLEMA: Cuando el cliente web guarda una factura, a veces no incluye sale_partner_id
        en los vals de las líneas (p.ej. columna opcional oculta en el navegador). El mecanismo
        de autocompletado (_move_autocomplete_invoice_lines_write) crea un objeto virtual basado
        en la BD y puede no incluir cambios explícitos en sale_partner_id.

        PROTECCIÓN: Capturamos los values EXPLÍCITOS de sale_partner_id que el cliente envía
        (tanto para líneas UPDATE cmd=1 como para líneas NUEVAS cmd=0) y, tras el write estándar,
        verificamos que se hayan aplicado correctamente.
        """
        # KLO. Extraer los sale_partner_id EXPLÍCITOS enviados por el cliente
        # para líneas EXISTENTES (cmd=1). Los usaremos para verificar después del write.
        explicit_sale_partners = {}  # {line_id: sale_partner_id}
        # KLO. Para líneas NUEVAS (cmd=0): guardar los sale_partner_id en orden de aparición.
        # Si el autocompletado de Odoo elimina el campo antes de llamar a create(),
        # lo re-aplicamos tras el write identificando las líneas recién creadas.
        new_line_sale_partners = []  # [(sale_partner_id,)] en orden de cmd=0
        for key in ('invoice_line_ids', 'line_ids'):
            for cmd in vals.get(key, []):
                if isinstance(cmd, (list, tuple)) and len(cmd) >= 3:
                    cmd_type, line_id, cmd_vals = cmd[0], cmd[1], cmd[2]
                    if isinstance(cmd_vals, dict):
                        if cmd_type == 1 and 'sale_partner_id' in cmd_vals:
                            # KLO. El cliente envió explícitamente un sale_partner_id para esta línea
                            explicit_sale_partners[line_id] = cmd_vals['sale_partner_id']
                        elif cmd_type == 0 and 'sale_partner_id' in cmd_vals:
                            # KLO. Línea nueva con sale_partner_id explícito
                            new_line_sale_partners.append(cmd_vals['sale_partner_id'])

        # KLO. Capturar IDs de líneas existentes antes del write para identificar las nuevas después
        existing_line_ids = set()
        if new_line_sale_partners:
            for move in self:
                existing_line_ids.update(move.line_ids.ids)

        result = super().write(vals)

        # KLO. Verificar y re-aplicar los sale_partner_id explícitos del cliente
        # en líneas EXISTENTES, en caso de que el autocompletado los haya perdido
        if explicit_sale_partners:
            for line_id, spid in explicit_sale_partners.items():
                line = self.env['account.move.line'].browse(line_id)
                if line.exists():
                    current_spid = line.sale_partner_id.id or False
                    expected_spid = spid or False
                    if current_spid != expected_spid:
                        _logger.warning(
                            "KLO PROTECCIÓN: sale_partner_id no se guardó correctamente en línea %s. "
                            "Esperado=%s, Actual=%s. Re-aplicando...",
                            line_id, expected_spid, current_spid,
                        )
                        # KLO. Llamar directamente a super().write para evitar recursión
                        self.env['account.move.line'].browse(line_id).write(
                            {'sale_partner_id': expected_spid}
                        )

        # KLO. Re-aplicar sale_partner_id en líneas NUEVAS (cmd=0) por si el autocompletado
        # eliminó el campo antes de llamar a create(). Se emparejan por orden de creación.
        if new_line_sale_partners:
            idx = 0
            for move in self:
                new_lines = move.line_ids.filtered(lambda l: l.id not in existing_line_ids)
                for line in new_lines:
                    if idx >= len(new_line_sale_partners):
                        break
                    expected_spid = new_line_sale_partners[idx] or False
                    current_spid = line.sale_partner_id.id or False
                    if current_spid != expected_spid:
                        _logger.warning(
                            "KLO PROTECCIÓN (nueva línea): sale_partner_id no se guardó en línea %s. "
                            "Esperado=%s, Actual=%s. Re-aplicando...",
                            line.id, expected_spid, current_spid,
                        )
                        line.write({'sale_partner_id': expected_spid})
                    idx += 1

        return result

    def action_post(self):
        """KLO. Tras validar la factura:
        1. Elimina las líneas analíticas creadas por account_analytic_distribution (AvanzOSC)
           que tengan amount=0 pero cuya línea de factura tenga balance≠0. Estas líneas son
           inútiles y se producen cuando el analytic_template tiene percentage=0.0.
        2. Propaga sale_partner_id de cada línea de factura al campo partner_id de las
           líneas analíticas válidas creadas por el template (account_move_id = factura).
        """
        result = super().action_post()
        for move in self:
            # KLO. Las líneas creadas por AvanzOSC están en analytic_line_ids (account_move_id = move.id)
            # Su move_id apunta a la línea de factura (account.move.line).
            lines_to_delete = move.analytic_line_ids.filtered(
                lambda al: al.amount == 0.0 and al.move_id and al.move_id.balance != 0.0
            )
            if lines_to_delete:
                lines_to_delete.unlink()
            # KLO. Propagar sale_partner_id → partner_id en las líneas del template que quedan
            for analytic_line in move.analytic_line_ids:
                invoice_line = analytic_line.move_id
                if invoice_line and invoice_line.sale_partner_id and not analytic_line.partner_id:
                    analytic_line.partner_id = invoice_line.sale_partner_id
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # KLO. Campo "Cliente de venta" en la línea de factura de compra.
    # Campo simple (sin compute, sin onchange) para garantizar que ninguna operación automática
    # (guardar, confirmar) sobreescriba el valor asignado manualmente en cada línea.
    # La propagación inicial se hace SOLO en create(): prioridad pedido → cabecera.
    sale_partner_id = fields.Many2one(
        'res.partner',
        string='Cliente de venta',
    )

    @api.model
    def default_get(self, fields_list):
        """KLO. Asigna sale_partner_id por defecto desde la cabecera de la factura al añadir una línea nueva.

        En la UI, el valor llega vía 'default_sale_partner_id' en el contexto del campo invoice_line_ids
        (definido en la vista KLO de klo_view_move_invoice_line_context). Odoo base lo procesa
        automáticamente antes de llegar aquí.

        Este método actúa como fallback para creación programática donde se pase 'default_move_id'
        en el contexto pero no 'default_sale_partner_id'.
        """
        defaults = super().default_get(fields_list)
        if 'sale_partner_id' not in defaults:
            # KLO. Fallback: buscar desde default_move_id cuando no viene default_sale_partner_id
            move_id = self.env.context.get('default_move_id') or self.env.context.get('move_id')
            if move_id:
                move = self.env['account.move'].browse(move_id)
                if move.sale_partner_id:
                    defaults['sale_partner_id'] = move.sale_partner_id.id
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """KLO. Al crear líneas de factura, asignar sale_partner_id si no viene informado.
        Prioridad: 1) línea del pedido de compra, 2) cabecera de la factura.

        NOTA: Solo se intenta asignar automáticamente cuando 'sale_partner_id' NO está presente
        en vals. Si ya viene con cualquier valor (incluyendo False para limpiar explícitamente),
        se respeta sin modificación. Esto evita sobreescribir valores que el usuario ha fijado
        manualmente en líneas nuevas antes de guardarlas por primera vez.
        """
        for vals in vals_list:
            if 'sale_partner_id' not in vals:
                # KLO. Prioridad 1: línea del pedido de compra
                purchase_line_id = vals.get('purchase_line_id')
                if purchase_line_id:
                    purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                    if purchase_line.sale_partner_id:
                        vals['sale_partner_id'] = purchase_line.sale_partner_id.id
                        continue
                # KLO. Prioridad 2: cabecera de la factura
                move_id = vals.get('move_id')
                if move_id:
                    move = self.env['account.move'].browse(move_id)
                    if move.sale_partner_id:
                        vals['sale_partner_id'] = move.sale_partner_id.id
        return super().create(vals_list)

    @api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.journal_id')
    def _compute_analytic_account_id(self):
        """KLO. Override para añadir cadena de fallback en la asignación de cuenta analítica.

        Prioridad:
        1) Regla analítica por cuenta contable del artículo / categoría (estándar Odoo via account.analytic.default)
        2) Regla analítica por cuenta por defecto del diario (fallback KLO)

        Esto asegura que si no hay regla en account.analytic.default para la cuenta contable del artículo,
        se intente con la cuenta por defecto del diario de la factura.
        """
        # KLO. Paso 1: Lógica estándar de Odoo
        super()._compute_analytic_account_id()

        # KLO. Paso 2: Fallback - si no se asignó cuenta analítica, buscar por cuenta del diario
        for record in self:
            if record.analytic_account_id:
                continue  # KLO. Ya tiene cuenta analítica, no hace falta buscar más

            if record.exclude_from_invoice_tab and record.move_id.is_invoice(include_receipts=True):
                continue  # KLO. Excluir líneas que no son de la pestaña de factura

            journal_default_account = record.move_id.journal_id.default_account_id
            if not journal_default_account:
                continue

            partner_id = (
                record.partner_id.commercial_partner_id.id
                or (record.move_id.partner_id and record.move_id.partner_id.commercial_partner_id.id)
            )

            rec = self.env['account.analytic.default'].account_get(
                product_id=record.product_id.id,
                partner_id=partner_id,
                account_id=journal_default_account.id,
                user_id=record.env.uid,
                date=record.date,
                company_id=record.move_id.company_id.id,
            )
            if rec:
                record.analytic_account_id = rec.analytic_id  # KLO. Fallback: cuenta del diario

    def _prepare_analytic_line(self):
        """KLO. Override para propagar sale_partner_id al campo partner_id de las líneas analíticas (analytic_account_id)."""
        result = super()._prepare_analytic_line()
        for i, move_line in enumerate(self):
            if move_line.sale_partner_id and i < len(result):
                # KLO. El "Cliente de venta" de la línea de factura se asigna como partner_id del apunte analítico
                result[i]['partner_id'] = move_line.sale_partner_id.id
        return result

    def _prepare_analytic_distribution_line(self, distribution):
        """KLO. Override para propagar sale_partner_id al campo partner_id de las líneas analíticas (distribución de etiquetas)."""
        result = super()._prepare_analytic_distribution_line(distribution)
        if self.sale_partner_id:
            # KLO. El "Cliente de venta" de la línea de factura se asigna como partner_id del apunte analítico
            result['partner_id'] = self.sale_partner_id.id
        return result

