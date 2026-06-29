# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    whatsapp_phone = fields.Char(
        string="Teléfono WhatsApp",
        copy=False,
        help=(
            "Número en formato E.164 (ej. +34612345678). "
            "Usado para autenticar al cliente en el canal WhatsApp."
        ),
    )
    whatsapp_order_enabled = fields.Boolean(
        string="Pedidos por WhatsApp activos",
        default=False,
        help="Si está marcado, este contacto puede realizar pedidos por WhatsApp.",
    )

    _sql_constraints = [
        (
            "whatsapp_phone_unique",
            "UNIQUE(whatsapp_phone)",
            "Ya existe un contacto con ese número WhatsApp.",
        )
    ]
