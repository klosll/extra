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
        """KLO. Override para:
        1. Propagar sale_partner_id de la línea del pedido a la línea de factura.
        2. Pre-computar analytic_account_id desde la cuenta contable del artículo/categoría,
           con fallback a la cuenta por defecto del diario, cuando el pedido no tiene analítica asignada.
           Esto garantiza que la cuenta analítica se rellene correctamente incluso si
           account.analytic.default no tiene una regla por producto/proveedor.
        """
        result = super()._prepare_account_move_line(move=move)

        # KLO. Propagar sale_partner_id
        if self.sale_partner_id:
            result['sale_partner_id'] = self.sale_partner_id.id

        # KLO. Si el pedido de compra no tenía cuenta analítica, calcularla
        # desde la cuenta contable del artículo (igual que hará _compute_analytic_account_id
        # en la línea de factura). Esto asegura el valor correcto en el momento de creación.
        if not result.get('analytic_account_id') and not self.display_type and self.product_id:
            company = self.company_id
            fiscal_pos = self.order_id.fiscal_position_id
            # Obtener la cuenta de gastos del artículo (o categoría si no tiene propia)
            accounts = self.product_id.product_tmpl_id.with_company(company).get_product_accounts(fiscal_pos=fiscal_pos)
            expense_account = accounts.get('expense')

            # Fallback a la cuenta por defecto del diario si el artículo no tiene cuenta de gastos
            if not expense_account and move:
                expense_account = move.journal_id.default_account_id

            if expense_account:
                date = (move.date if move else
                        (self.order_id.date_order and self.order_id.date_order.date()))
                rec = self.env['account.analytic.default'].account_get(
                    product_id=self.product_id.id,
                    partner_id=self.order_id.partner_id.id,
                    account_id=expense_account.id,
                    user_id=self.env.uid,
                    date=date,
                    company_id=company.id,
                )
                if rec:
                    result['analytic_account_id'] = rec.analytic_id.id  # KLO. Asignar desde regla analítica

        return result


