# KLO — Pedidos por WhatsApp con IA

## Módulo

| Campo | Valor |
|---|---|
| Name | `klo_whatsapp_order` |
| Version | `18.0.4.0.0` |
| Author | `KLO Ingenieria Informatica S.L.L.` |
| License | `AGPL-3` |
| Path | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_whatsapp_order` |

## Descripción

Este módulo habilita la recepción automatizada de pedidos de clientes por WhatsApp usando un canal de WhatsApp (Meta Cloud API o OpenWA) y un proveedor de IA (Xiaomi MiMo V2.5, OpenAI o Groq) como capa de interpretación del lenguaje natural. El objetivo es convertir mensajes libres del cliente en borradores de pedidos de venta en Odoo, manteniendo trazabilidad de la conversación, control de confirmación y seguimiento del consumo de IA.

**Canales de WhatsApp soportados:**
- **Meta Cloud API** (WhatsApp Business): API oficial, requiere cuenta de negocio de Facebook.
- **OpenWA** (Self-Hosted): Gateway open source auto-hospedado con Docker, usa WhatsApp Web, gratuito.

**Proveedores de IA soportados:**
- **Xiaomi MiMo V2.5** (recomendado): API compatible con OpenAI, coste reducido. Modelos: `mimo-v2.5`, `mimo-v2.5-pro`.
- **OpenAI** (pago): Modelos GPT-4o, GPT-4o-mini, GPT-4-turbo.
- **Groq** (gratis para pruebas): API gratuita con modelos Llama. Modelos: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`.

### `res.config.settings` (hereda `sale.res_config_settings_view_form`)

| Campo | Tipo | Etiqueta | Descripción |
|---|---|---|---|
| `wa_channel` | `Selection` | Canal de WhatsApp | Selecciona proveedor: `meta` (Cloud API) o `openwa` (Self-Hosted). |
| `wa_verify_token` | `Char` | Token de verificación webhook | Token de verificación de Meta. |
| `wa_access_token` | `Char` | Access Token Meta | Token permanente de la WhatsApp Business Cloud API. |
| `wa_phone_number_id` | `Char` | Phone Number ID | ID del número de teléfono en Meta. |
| `wa_api_version` | `Char` | Versión API Meta | Versión de la API (default: v19.0). |
| `openwa_base_url` | `Char` | URL base OpenWA | Endpoint del servidor OpenWA (default: http://localhost:2785). |
| `openwa_api_key` | `Char` | API Key OpenWA | Clave de API generada por OpenWA. |
| `openwa_session_id` | `Char` | Session ID de OpenWA | ID de la sesión de WhatsApp en OpenWA. |
| `openwa_webhook_secret` | `Char` | Secret HMAC (webhook OpenWA) | Secreto para verificar firma HMAC de webhooks entrantes. |
| `use_mimo` | `Selection` | Proveedor de IA | Selecciona proveedor: `mimo` (MiMo), `openai` (OpenAI) o `groq` (Groq gratis). |
| `mimo_api_key` | `Char` | API Key MiMo | Clave de API de Xiaomi MiMo. |
| `mimo_model` | `Char` | Modelo MiMo | Modelo a usar (default: mimo-v2.5). |
| `mimo_base_url` | `Char` | URL base API MiMo | Endpoint de MiMo (default: https://api.xiaomimimo.com/v1). |
| `openai_api_key` | `Char` | API Key OpenAI | Clave de API de OpenAI. |
| `openai_model` | `Char` | Modelo OpenAI | Modelo OpenAI (default: gpt-4o). |
| `groq_api_key` | `Char` | API Key Groq | Clave de API de Groq (gratis en console.groq.com). |
| `groq_model` | `Char` | Modelo Groq | Modelo Groq (default: llama-3.3-70b-versatile). |
| `wa_max_tokens_per_day` | `Integer` | Límite diario de tokens | 0 = sin límite. |
| `wa_max_cost_per_month` | `Float` | Límite mensual de coste IA (€) | 0 = sin límite. |
| `wa_auto_confirm_order` | `Boolean` | Confirmar pedido automáticamente | Sin validación al cliente. |
| `wa_order_team_id` | `Many2one(crm.team)` | Equipo de ventas predeterminado | Equipo para los pedidos generados. |
| `wa_session_timeout_hours` | `Integer` | Tiempo expiración sesión (horas) | Default: 24. |

## Campos añadidos

### `res.partner`

| Campo | Tipo | Etiqueta | Descripción |
|---|---|---|---|
| `whatsapp_phone` | `Char` | Teléfono WhatsApp | Número en formato E.164 usado para autenticar el canal. |
| `whatsapp_order_enabled` | `Boolean` | Pedidos por WhatsApp activos | Habilita al contacto para operar por WhatsApp. |

### `klo.whatsapp.session`

| Campo | Tipo | Etiqueta | Descripción |
|---|---|---|---|
| `partner_id` | `Many2one(res.partner)` | Cliente | Cliente asociado a la conversación. |
| `wa_phone_number` | `Char` | Número WhatsApp | Número origen de la sesión. |
| `state` | `Selection` | Estado | Flujo de sesión: abierta, esperando confirmación, completada o cancelada. |
| `history_json` | `Text` | Historial JSON | Historial compacto para contexto del modelo de IA. |
| `draft_order_id` | `Many2one(sale.order)` | Pedido borrador | Pedido generado a partir de la conversación. |
| `whatsapp_message_ids` | `One2many(klo.whatsapp.message)` | Mensajes WhatsApp | Mensajes entrantes y salientes asociados. |
| `ai_usage_ids` | `One2many(klo.whatsapp.ai.usage)` | Uso IA | Consumos de OpenAI vinculados a la sesión. |
| `message_count` | `Integer` | Nº mensajes | Total de mensajes registrados. |
| `total_tokens` | `Integer` | Tokens totales | Tokens acumulados en la sesión. |

### `klo.whatsapp.message`

| Campo | Tipo | Etiqueta | Descripción |
|---|---|---|---|
| `session_id` | `Many2one(klo.whatsapp.session)` | Sesión | Relación con la conversación. |
| `direction` | `Selection` | Dirección | Entrante o saliente. |
| `body` | `Text` | Cuerpo | Texto del mensaje. |
| `wa_message_id` | `Char` | ID mensaje Meta | Identificador devuelto por Meta para el mensaje entrante. |
| `raw_payload` | `Text` | Payload raw (debug) | Fragmento recibido para diagnóstico. |
| `processing_error` | `Text` | Error de procesamiento | Incidencia ocurrida durante el tratamiento del mensaje. |

### `klo.whatsapp.ai.usage`

| Campo | Tipo | Etiqueta | Descripción |
|---|---|---|---|
| `session_id` | `Many2one(klo.whatsapp.session)` | Sesión | Sesión vinculada al consumo. |
| `model_name` | `Char` | Modelo IA | Modelo OpenAI utilizado. |
| `prompt_tokens` | `Integer` | Tokens de entrada | Tokens consumidos por el prompt. |
| `completion_tokens` | `Integer` | Tokens de salida | Tokens consumidos por la respuesta. |
| `total_tokens` | `Integer` | Tokens totales | Suma automática de entrada y salida. |
| `estimated_cost_eur` | `Float` | Coste estimado (€) | Estimación de coste basada en tarifas orientativas. |

## Dependencias

### Módulos Odoo

- `sale_stock`
- `sale_management`
- `base_setup`
- `queue_job`

### Paquetes Python externos

- `openai` (usado tanto para OpenAI como para MiMo, que es compatible)
- `requests`

## Lógica

- **Webhook de WhatsApp**: `controllers/whatsapp_webhook.py` expone dos endpoints:
  - `/webhook/whatsapp` (GET/POST): Verificación y recepción de Meta Cloud API.
  - `/webhook/openwa` (POST): Recepción de OpenWA con verificación HMAC (`X-Hub-Signature-256`).
- **Routing de canal**: `_get_wa_sender(channel)` selecciona el servicio de envío (`meta_api` o `openwa_api`) según el canal configurado.
- **Sesión**: `_process_incoming_payload` (Meta) y `_handle_incoming_text` (ambos canales) localizan o crean la sesión activa del cliente.
- **Autenticación del cliente**: solo se aceptan números presentes en `res.partner.whatsapp_phone` y con `whatsapp_order_enabled` activo.
- **Historial conversacional**: `append_message()` mantiene un contexto compacto para la IA.
- **Control de gasto**: `_check_daily_limits()` consulta `klo.whatsapp.ai.usage` y bloquea cuando se superan límites diarios o mensuales.
- **Routing de proveedor IA**: `openai_service._get_client_and_model()` selecciona MiMo, OpenAI o Groq según `use_mimo`. Todos usan la librería `openai` con diferente `base_url`.
- **Interpretación con IA**: `services/openai_service.py` llama al proveedor configurado, obliga una respuesta JSON y registra consumo por sesión.
- **Construcción del pedido**: `services/order_builder.py` genera o actualiza el borrador de `sale.order` aplicando la tarifa del cliente.
- **Confirmación**: el flujo puede requerir validación del cliente o confirmar automáticamente según configuración.
- **Servicios WhatsApp**: `services/meta_api.py` (Cloud API) y `services/openwa_api.py` (OpenWA) encapsulan el envío de mensajes, verificación de webhooks y consulta de estado de sesión/QR.

## Vistas modificadas

- **Formulario de contactos** (`base.view_partner_form`): añade `whatsapp_phone` y `whatsapp_order_enabled` a continuación del campo `category_id` (etiquetas), usando el XPath `//field[@name='category_id']` con `position="after"`.
- **Ajustes de ventas** (`sale.res_config_settings_view_form`): añade bloque de configuración con selector de canal (Meta/OpenWA), selector de proveedor IA (MiMo/OpenAI/Groq), secciones condicionales para cada proveedor, límites de gasto y comportamiento de pedidos.
- **Menús bajo Ventas**: nuevo nodo **WhatsApp IA** con accesos a sesiones, mensajes y uso de IA.

## Estructura de archivos

```text
klo_whatsapp_order/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── whatsapp_webhook.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py
│   ├── whatsapp_ai_usage.py
│   ├── whatsapp_config.py
│   ├── whatsapp_message.py
│   └── whatsapp_session.py
├── services/
│   ├── __init__.py
│   ├── meta_api.py
│   ├── openai_service.py
│   ├── openwa_api.py
│   └── order_builder.py
├── security/
│   ├── ir.model.access.csv
│   └── whatsapp_order_security.xml
├── views/
│   ├── res_partner_views.xml
│   ├── whatsapp_ai_usage_views.xml
│   ├── whatsapp_config_views.xml
│   ├── whatsapp_message_views.xml
│   ├── whatsapp_order_menus.xml
│   └── whatsapp_session_views.xml
├── data/
│   └── ir_config_parameter_data.xml
└── static/
    └── description/
        ├── icon.png
        ├── Manual_de_uso_klo_whatsapp_order.md
        ├── Manual_de_uso_klo_whatsapp_order.pdf
        └── Technical_context.md
```

## Instalación / Actualización

```bash
cd /opt/odoo18_desarrollo/odoo
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d garridomontero_dev -i klo_whatsapp_order --stop-after-init

/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d garridomontero_dev -u klo_whatsapp_order --stop-after-init
```

## Posibles adaptaciones futuras

- **Multiempresa**: parametrizar credenciales Meta/MiMo/OpenAI por compañía.
- **Rate limiting**: añadir límites por partner, por número y por ventana temporal.
- **Fallback humano**: derivar sesiones dudosas a un comercial o cola de soporte.
- **RGPD**: anonimización, retención limitada del histórico y consentimiento explícito del canal.
- **Thinking de MiMo**: habilitar `thinking` para `mimo-v2.5-pro` en tareas complejas de interpretación.
