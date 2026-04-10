# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # KLO. Campo "Cliente de venta" en la línea de factura de compra.
    # Se inicializa con el valor de la cabecera account.move.sale_partner_id pero es editable.
    sale_partner_id = fields.Many2one(
        'res.partner',
        string='Cliente de venta',
        compute='_compute_sale_partner_id',
        store=True,
        readonly=False,
    )

    @api.depends('move_id.sale_partner_id', 'purchase_line_id.sale_partner_id')
    def _compute_sale_partner_id(self):
        for line in self:
            # KLO. Solo asigna si la línea aún no tiene valor propio guardado
            if not line._origin.sale_partner_id:
                # KLO. Prioridad: 1) línea del pedido de compra, 2) cabecera de la factura
                if line.purchase_line_id and line.purchase_line_id.sale_partner_id:
                    line.sale_partner_id = line.purchase_line_id.sale_partner_id
                else:
                    line.sale_partner_id = line.move_id.sale_partner_id

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
        """KLO. Override para propagar sale_partner_id a las líneas analíticas creadas por analytic_account_id."""
        result = super()._prepare_analytic_line()
        for i, move_line in enumerate(self):
            if move_line.sale_partner_id and i < len(result):
                result[i]['sale_partner_id'] = move_line.sale_partner_id.id
        return result

    def _prepare_analytic_distribution_line(self, distribution):
        """KLO. Override para propagar sale_partner_id a las líneas analíticas creadas por distribución de etiquetas."""
        result = super()._prepare_analytic_distribution_line(distribution)
        if self.sale_partner_id:
            result['sale_partner_id'] = self.sale_partner_id.id
        return result
