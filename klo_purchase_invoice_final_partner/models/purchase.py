# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['sale_partner_id'] = self.sale_partner_id.id
        return invoice_vals


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # KLO. Campo "Cliente de venta" en la línea de pedido de compra.
    # Se inicializa con el valor de la cabecera purchase.order.sale_partner_id pero es editable.
    sale_partner_id = fields.Many2one(
        'res.partner',
        string='Cliente de venta',
        compute='_compute_sale_partner_id',
        store=True,
        readonly=False,
    )

    @api.depends('order_id.sale_partner_id')
    def _compute_sale_partner_id(self):
        for line in self:
            # KLO. Solo asigna si la línea aún no tiene valor propio guardado
            if not line._origin.sale_partner_id:
                line.sale_partner_id = line.order_id.sale_partner_id

    def _prepare_account_move_line(self, move=False):
        """KLO. Propaga sale_partner_id de la línea del pedido a la línea de factura."""
        result = super()._prepare_account_move_line(move=move)

        # KLO. Propagar sale_partner_id
        if self.sale_partner_id:
            result['sale_partner_id'] = self.sale_partner_id.id

        return result
