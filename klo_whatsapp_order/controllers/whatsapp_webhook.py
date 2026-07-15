# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsappWebhookController(http.Controller):

    # =====================================================================
    # Meta Cloud API Webhooks
    # =====================================================================

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
            _logger.debug("WhatsApp Meta payload: %s", payload)
            request.env["klo.whatsapp.session"].sudo().with_delay(
                description="Procesar mensaje WhatsApp Meta entrante"
            )._process_incoming_payload(payload, channel="meta")
        except Exception:
            _logger.exception("Error al encolar mensaje WhatsApp Meta")
        return request.make_json_response({"status": "ok"})

    # =====================================================================
    # OpenWA Webhooks
    # =====================================================================

    @http.route(
        "/webhook/openwa",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def receive_openwa_message(self, **kwargs):
        """
        Recibe mensajes entrantes de OpenWA.
        OpenWA envía eventos con esta estructura:
        {
            "event": "message.received",
            "session": "session-id",
            "data": {
                "id": "...",
                "from": "phone@c.us",
                "to": "bot-phone@c.us",
                "body": "texto del mensaje",
                "type": "text",
                "timestamp": 1234567890,
                "fromMe": false,
                ...
            }
        }
        """
        try:
            raw_body = request.httprequest.data or b"{}"
            payload = json.loads(raw_body)

            # Verificar firma HMAC si está configurada
            icp = request.env["ir.config_parameter"].sudo()
            webhook_secret = icp.get_param("klo_whatsapp_order.openwa_webhook_secret")
            if webhook_secret:
                from ..services import openwa_api

                signature = request.httprequest.headers.get("X-Hub-Signature-256")
                if not openwa_api.verify_webhook_signature(raw_body, signature, webhook_secret):
                    _logger.warning("Firma HMAC inválida en webhook OpenWA")
                    return request.make_response("Unauthorized", status=401)

            event = payload.get("event", "")
            _logger.debug("OpenWA event: %s, payload: %s", event, payload)

            # Solo procesar eventos de mensajes entrantes
            if event == "message.received":
                data = payload.get("data", {})
                # Ignorar mensajes enviados por el bot
                if data.get("fromMe", False):
                    return request.make_json_response({"status": "ok"})

                # Extraer número del chatId (formato: phone@c.us)
                chat_id = data.get("chatId", data.get("from", ""))
                from_number = chat_id.replace("@c.us", "").replace("@s.whatsapp.net", "")

                text = data.get("body", "")
                wa_msg_id = data.get("id", data.get("waMessageId", ""))

                if not from_number or data.get("type") != "text":
                    return request.make_json_response({"status": "ok"})

                request.env["klo.whatsapp.session"].sudo().with_delay(
                    description="Procesar mensaje OpenWA entrante"
                )._handle_incoming_text(
                    from_number,
                    wa_msg_id,
                    text,
                    raw_payload=data,
                    channel="openwa",
                )

        except Exception:
            _logger.exception("Error al procesar webhook OpenWA")

        return request.make_json_response({"status": "ok"})

    # =====================================================================
    # Endpoint auxiliar para verificar estado de OpenWA
    # =====================================================================

    @http.route(
        "/webhook/openwa/status",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def openwa_status(self, **kwargs):
        """Endpoint interno para verificar el estado de la sesión OpenWA."""
        from ..services import openwa_api

        session_info = openwa_api.check_session_status(request.env)
        return request.make_json_response(session_info)
