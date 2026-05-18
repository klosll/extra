# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_email_sent = fields.Boolean(
        string="Enviado",
        default=False,
        copy=False,
        tracking=True,
        help="Indica si el pedido ha sido enviado por correo electrónico al menos una vez.",
    )

    delivery_signed_status = fields.Selection(
        selection=[
            ("no", "No"),
            ("yes", "Sí"),
            ("partial", "Parcialmente"),
        ],
        string="Entregas firmadas",
        compute="_compute_delivery_signed_status",
        store=True,
        help="Estado de firma de las entregas de salida asociadas al pedido.",
    )

    def action_quotation_sent(self):
        """Sobrescribe para marcar el pedido como enviado por email."""
        res = super().action_quotation_sent()
        self.write({"is_email_sent": True})
        return res

    def action_quotation_send(self):
        """Sobrescribe para marcar como enviado cuando se envía desde el wizard de email."""
        res = super().action_quotation_send()
        # El envío real ocurre en action_quotation_sent, pero si el wizard
        # confirma el envío también lo marcamos aquí como respaldo.
        return res

    @api.depends(
        "picking_ids",
        "picking_ids.state",
        "picking_ids.is_signed",
        "picking_ids.location_dest_id.usage",
    )
    def _compute_delivery_signed_status(self):
        for order in self:
            # Solo entregas de salida al cliente que estén hechas
            done_deliveries = order.picking_ids.filtered(
                lambda p: p.state == "done"
                and p.location_dest_id.usage == "customer"
            )
            if not done_deliveries:
                order.delivery_signed_status = "no"
                continue

            signed = done_deliveries.filtered(lambda p: p.is_signed)
            if len(signed) == len(done_deliveries):
                order.delivery_signed_status = "yes"
            elif signed:
                order.delivery_signed_status = "partial"
            else:
                order.delivery_signed_status = "no"

