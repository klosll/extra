# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['sale_partner_id'] = self.sale_partner_id.id
        return invoice_vals
