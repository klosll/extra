# Copyright 2025 KLO Ingeniería Informática S.L.L. (https://www.klo.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class KloAccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    # KLO. Campo "Cliente de venta" propagado desde la línea de factura de compra
    # al validar (action_post) a través de _prepare_analytic_distribution_line.
    sale_partner_id = fields.Many2one(
        'res.partner',
        string='Cliente de venta',
        index=True,
    )

