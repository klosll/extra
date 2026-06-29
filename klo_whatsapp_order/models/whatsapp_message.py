# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WhatsappMessage(models.Model):
    _name = "klo.whatsapp.message"
    _description = "Mensaje WhatsApp"
    _order = "create_date asc"

    session_id = fields.Many2one(
        "klo.whatsapp.session",
        string="Sesión",
        required=True,
        ondelete="cascade",
        index=True,
    )
    direction = fields.Selection(
        [("in", "Entrante"), ("out", "Saliente")],
        required=True,
        string="Dirección",
    )
    body = fields.Text(string="Cuerpo", required=True)
    wa_message_id = fields.Char(string="ID mensaje Meta", index=True)
    raw_payload = fields.Text(string="Payload raw (debug)")
    processing_error = fields.Text(string="Error de procesamiento")
