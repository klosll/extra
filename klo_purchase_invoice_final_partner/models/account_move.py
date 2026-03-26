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

    @api.depends('move_id.sale_partner_id')
    def _compute_sale_partner_id(self):
        for line in self:
            # KLO. Solo asigna si la línea aún no tiene valor propio guardado
            if not line._origin.sale_partner_id:
                line.sale_partner_id = line.move_id.sale_partner_id

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
