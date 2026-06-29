# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

_logger = logging.getLogger(__name__)
META_API_BASE = "https://graph.facebook.com/{version}/{phone_number_id}/messages"


def send_text_message(env, to_number, body):
    """Envía un mensaje de texto por WhatsApp usando la Meta Cloud API."""
    icp = env["ir.config_parameter"].sudo()
    token = icp.get_param("klo_whatsapp_order.access_token")
    phone_id = icp.get_param("klo_whatsapp_order.phone_number_id")
    version = icp.get_param("klo_whatsapp_order.api_version", "v19.0")

    if not token or not phone_id:
        _logger.warning("Meta API no configurada (token o phone_id ausentes)")
        return {}

    url = META_API_BASE.format(version=version, phone_number_id=phone_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        _logger.error("Error enviando mensaje WhatsApp a %s: %s", to_number, exc)
        return {}
