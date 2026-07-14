# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

_logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Eres un asistente de pedidos para una empresa distribuidora.
Recibes mensajes de un cliente en lenguaje natural (español) y debes extraer los artículos
que quiere pedir.

CATÁLOGO DISPONIBLE (JSON):
{catalog_json}

INSTRUCCIONES:
- Responde SIEMPRE en JSON válido con este esquema:
  {{
    "intent": "order" | "query_stock" | "query_price" | "cancel" | "confirm" | "other",
    "lines": [
      {{"product_id": <int>, "qty": <float>, "note": "<texto opcional>"}}
    ],
    "message_to_customer": "<mensaje amigable en español para el cliente>"
  }}
- Solo puedes incluir product_id que estén en el catálogo proporcionado.
- Si el cliente pide algo no disponible, inclúyelo en message_to_customer e ignóralo en lines.
- Nunca inventes precios; los precios los calculará el sistema.
- Si el mensaje es ambiguo, solicita aclaración en message_to_customer y devuelve lines vacío.
- No menciones datos de otros clientes ni de pedidos ajenos.
"""


def _get_client_and_model(env):
    """
    Determina el proveedor de IA a usar según la configuración.
    Devuelve (client, model_name, provider_name).
    """
    from openai import OpenAI

    icp = env["ir.config_parameter"].sudo()
    use_mimo = icp.get_param("klo_whatsapp_order.use_mimo", "True")

    if use_mimo == "True" or use_mimo is True:
        api_key = icp.get_param("klo_whatsapp_order.mimo_api_key")
        model = icp.get_param("klo_whatsapp_order.mimo_model", "mimo-v2.5")
        base_url = icp.get_param(
            "klo_whatsapp_order.mimo_base_url", "https://api.xiaomimimo.com/v1"
        )
        if not api_key:
            raise ValueError(
                "La API Key de Xiaomi MiMo no está configurada. "
                "Configure 'API Key MiMo' en Ajustes > Ventas > Pedidos por WhatsApp."
            )
        client = OpenAI(api_key=api_key, base_url=base_url)
        provider = "mimo"
        _logger.info("Usando proveedor MiMo (modelo: %s)", model)
    else:
        api_key = icp.get_param("klo_whatsapp_order.openai_api_key")
        model = icp.get_param("klo_whatsapp_order.openai_model", "gpt-4o")
        if not api_key:
            raise ValueError(
                "La API Key de OpenAI no está configurada. "
                "Configure 'API Key OpenAI' en Ajustes > Ventas > Pedidos por WhatsApp."
            )
        client = OpenAI(api_key=api_key)
        provider = "openai"
        _logger.info("Usando proveedor OpenAI (modelo: %s)", model)

    return client, model, provider


def interpret_message(env, history, user_message, catalog, session_id=None):
    """
    Llama al proveedor de IA configurado (MiMo u OpenAI) con el historial
    de conversación y el catálogo restringido.
    Devuelve dict con: intent, lines, message_to_customer.
    También registra el uso de tokens en klo.whatsapp.ai.usage.
    """
    client, model, provider = _get_client_and_model(env)

    system_msg = SYSTEM_PROMPT.format(
        catalog_json=json.dumps(catalog, ensure_ascii=False)
    )
    messages = [{"role": "system", "content": system_msg}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": user_message})

    kwargs = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    response = client.chat.completions.create(**kwargs)
    raw = response.choices[0].message.content or "{}"
    result = json.loads(raw)

    usage = response.usage
    if usage:
        try:
            env["klo.whatsapp.ai.usage"].sudo().create(
                {
                    "session_id": session_id,
                    "model_name": model,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                }
            )
        except Exception:
            _logger.warning("No se pudo registrar el uso de IA", exc_info=True)

    return result
