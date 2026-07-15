# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import hmac
import logging

import requests

_logger = logging.getLogger(__name__)


def _get_config(env):
    """Obtiene la configuración de OpenWA desde ir.config_parameter."""
    icp = env["ir.config_parameter"].sudo()
    base_url = icp.get_param("klo_whatsapp_order.openwa_base_url", "http://localhost:2785")
    api_key = icp.get_param("klo_whatsapp_order.openwa_api_key")
    session_id = icp.get_param("klo_whatsapp_order.openwa_session_id")
    return base_url.rstrip("/"), api_key, session_id


def send_text_message(env, to_number, body):
    """
    Envía un mensaje de texto por WhatsApp usando la API de OpenWA.

    Args:
        env: Odoo environment
        to_number: Número destino en formato internacional sin '+' (ej: 34612345678)
        body: Texto del mensaje (máx 4096 caracteres)

    Returns:
        dict con messageId y timestamp si es exitoso, dict vacío si falla
    """
    base_url, api_key, session_id = _get_config(env)

    if not api_key or not session_id:
        _logger.warning("OpenWA no configurada (api_key o session_id ausentes)")
        return {}

    # OpenWA usa el formato phone@c.us para el chatId
    chat_id = f"{to_number}@c.us"

    url = f"{base_url}/api/sessions/{session_id}/messages/send-text"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "chatId": chat_id,
        "text": body[:4096],  # OpenWA limita a 4096 caracteres
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        _logger.info(
            "Mensaje enviado vía OpenWA a %s: messageId=%s",
            to_number,
            result.get("messageId"),
        )
        return result
    except requests.RequestException as exc:
        _logger.error("Error enviando mensaje WhatsApp a %s via OpenWA: %s", to_number, exc)
        return {}


def verify_webhook_signature(payload_body, signature, secret):
    """
    Verifica la firma HMAC de un webhook entrante de OpenWA.

    Args:
        payload_body: Cuerpo raw del request (bytes)
        signature: Valor del header X-Hub-Signature-256
        secret: Secret configurado en el webhook

    Returns:
        True si la firma es válida, False en caso contrario
    """
    if not signature or not secret:
        return False

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def check_session_status(env):
    """
    Verifica el estado de la sesión de OpenWA.

    Returns:
        dict con el estado de la sesión o dict vacío si falla
    """
    base_url, api_key, session_id = _get_config(env)

    if not api_key or not session_id:
        return {}

    url = f"{base_url}/api/sessions/{session_id}"
    headers = {
        "X-API-Key": api_key,
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        _logger.error("Error verificando estado de sesión OpenWA: %s", exc)
        return {}


def get_qr_code(env):
    """
    Obtiene el código QR para autenticar la sesión de OpenWA.

    Returns:
        dict con qrCode (data:image/png;base64,...) y status, o dict vacío
    """
    base_url, api_key, session_id = _get_config(env)

    if not api_key or not session_id:
        return {}

    url = f"{base_url}/api/sessions/{session_id}/qr"
    headers = {
        "X-API-Key": api_key,
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        _logger.error("Error obteniendo QR de OpenWA: %s", exc)
        return {}
