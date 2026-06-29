# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsappWebhookController(http.Controller):

    @http.route(
        "/webhook/whatsapp",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def verify_webhook(self, **kwargs):
        """Meta llama a este endpoint con GET para verificar el webhook."""
        mode = kwargs.get("hub.mode")
        token = kwargs.get("hub.verify_token")
        challenge = kwargs.get("hub.challenge")
        stored_token = request.env["ir.config_parameter"].sudo().get_param(
            "klo_whatsapp_order.verify_token"
        )
        if mode == "subscribe" and token == stored_token:
            return request.make_response(
                challenge or "",
                headers=[("Content-Type", "text/plain")],
            )
        return request.make_response("Forbidden", status=403)

    @http.route(
        "/webhook/whatsapp",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def receive_message(self, **kwargs):
        """Recibe mensajes entrantes de Meta Cloud API."""
        try:
            payload = json.loads(request.httprequest.data or b"{}")
            _logger.debug("WhatsApp payload: %s", payload)
            request.env["klo.whatsapp.session"].sudo().with_delay(
                description="Procesar mensaje WhatsApp entrante"
            )._process_incoming_payload(payload)
        except Exception:
            _logger.exception("Error al encolar mensaje WhatsApp")
        return request.make_json_response({"status": "ok"})
