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
        """Sobrescribe para marcar el pedido como enviado por email (botón 'Marcar como enviado')."""
        res = super().action_quotation_sent()
        self.write({"is_email_sent": True})
        return res

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Sobrescribe message_post para detectar el envío real del email desde el wizard.

        Odoo 18: cuando el usuario pulsa 'Enviar' en el wizard de email del presupuesto,
        se llama a message_post con el contexto mark_so_as_sent=True.
        Este es el único punto fiable para capturar el envío real por correo.
        """
        res = super().message_post(**kwargs)
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state in ('draft', 'sent')).write({"is_email_sent": True})
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

