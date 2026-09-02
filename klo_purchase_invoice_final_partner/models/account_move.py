# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)

    def write(self, vals):
        """KLO. Proteger sale_partner_id en líneas contra sobreescritura al guardar."""
        # KLO. Extraer los sale_partner_id EXPLÍCITOS enviados por el cliente
        explicit_sale_partners = {}  # {line_id: sale_partner_id}
        new_line_sale_partners = []  # [(sale_partner_id,)] en orden de cmd=0
        for key in ('invoice_line_ids', 'line_ids'):
            for cmd in vals.get(key, []):
                if isinstance(cmd, (list, tuple)) and len(cmd) >= 3:
                    cmd_type, line_id, cmd_vals = cmd[0], cmd[1], cmd[2]
                    if isinstance(cmd_vals, dict):
                        if cmd_type == 1 and 'sale_partner_id' in cmd_vals:
                            explicit_sale_partners[line_id] = cmd_vals['sale_partner_id']
                        elif cmd_type == 0 and 'sale_partner_id' in cmd_vals:
                            new_line_sale_partners.append(cmd_vals['sale_partner_id'])

        existing_line_ids = set()
        if new_line_sale_partners:
            for move in self:
                existing_line_ids.update(move.line_ids.ids)

        result = super().write(vals)

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
                        self.env['account.move.line'].browse(line_id).write(
                            {'sale_partner_id': expected_spid}
                        )

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
           que tengan amount=0 pero cuya línea de factura tenga balance≠0.
        2. Propaga sale_partner_id de cada línea de factura al campo partner_id de las
           líneas analíticas válidas creadas por el template.
        """
        result = super().action_post()
        for move in self:
            # KLO. En v18 las líneas analíticas cuelgan de move.line_ids (no de move).
            lines_to_delete = move.line_ids.analytic_line_ids.filtered(
                lambda al: al.amount == 0.0 and al.move_line_id and al.move_line_id.balance != 0.0
            )
            if lines_to_delete:
                lines_to_delete.unlink()
            # KLO. Propagar sale_partner_id → partner_id en las líneas del template que quedan
            for analytic_line in move.line_ids.analytic_line_ids:
                invoice_line = analytic_line.move_line_id
                if invoice_line and invoice_line.sale_partner_id and not analytic_line.partner_id:
                    analytic_line.partner_id = invoice_line.sale_partner_id
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # KLO. Campo "Cliente de venta" en la línea de factura de compra.
    sale_partner_id = fields.Many2one(
        'res.partner',
        string='Cliente de venta',
    )

    @api.model
    def default_get(self, fields_list):
        """KLO. Asigna sale_partner_id por defecto desde la cabecera de la factura."""
        defaults = super().default_get(fields_list)
        if 'sale_partner_id' not in defaults:
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
        """
        for vals in vals_list:
            if 'sale_partner_id' not in vals:
                purchase_line_id = vals.get('purchase_line_id')
                if purchase_line_id:
                    purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                    if purchase_line.sale_partner_id:
                        vals['sale_partner_id'] = purchase_line.sale_partner_id.id
                        continue
                move_id = vals.get('move_id')
                if move_id:
                    move = self.env['account.move'].browse(move_id)
                    if move.sale_partner_id:
                        vals['sale_partner_id'] = move.sale_partner_id.id
        return super().create(vals_list)

    def _prepare_analytic_lines(self):
        """KLO. Override para propagar sale_partner_id al campo partner_id de las líneas analíticas."""
        result = super()._prepare_analytic_lines()
        # KLO. En v18 este método es ensure_one; propagamos a todas las líneas resultantes.
        if self.sale_partner_id:
            for line_vals in result:
                line_vals['partner_id'] = self.sale_partner_id.id
        return result

    def _prepare_analytic_distribution_line(self, distribution, account_ids, distribution_on_each_plan):
        """KLO. Override para propagar sale_partner_id al campo partner_id de las líneas analíticas (distribución)."""
        result = super()._prepare_analytic_distribution_line(
            distribution, account_ids, distribution_on_each_plan
        )
        if self.sale_partner_id:
            # KLO. El "Cliente de venta" de la línea de factura se asigna como partner_id del apunte analítico
            result['partner_id'] = self.sale_partner_id.id
        return result
