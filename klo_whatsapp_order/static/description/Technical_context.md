# KLO — Pedidos por WhatsApp con IA

## Módulo

| Campo | Valor |
|---|---|
| Name | `klo_whatsapp_order` |
| Version | `18.0.1.0.0` |
| Author | `KLO Ingenieria Informatica S.L.L.` |
| License | `AGPL-3` |
| Path | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_whatsapp_order` |

## Descripción

Este módulo habilita la recepción automatizada de pedidos de clientes por WhatsApp usando la Meta Cloud API como canal de entrada/salida y OpenAI como capa de interpretación del lenguaje natural. El objetivo es convertir mensajes libres del cliente en borradores de pedidos de venta en Odoo, manteniendo trazabilidad de la conversación, control de confirmación y seguimiento del consumo de IA.

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

- `openai`
- `requests`

## Lógica

- **Webhook de WhatsApp**: `controllers/whatsapp_webhook.py` verifica el endpoint con Meta y encola el tratamiento de cada POST.
- **Sesión**: `_process_incoming_payload` y `_handle_incoming_text` localizan o crean la sesión activa del cliente.
- **Autenticación del cliente**: solo se aceptan números presentes en `res.partner.whatsapp_phone` y con `whatsapp_order_enabled` activo.
- **Historial conversacional**: `append_message()` mantiene un contexto compacto para la IA.
- **Control de gasto**: `_check_daily_limits()` consulta `klo.whatsapp.ai.usage` y bloquea cuando se superan límites diarios o mensuales.
- **Interpretación con IA**: `services/openai_service.py` llama a OpenAI, obliga una respuesta JSON y registra consumo por sesión.
- **Construcción del pedido**: `services/order_builder.py` genera o actualiza el borrador de `sale.order` aplicando la tarifa del cliente.
- **Confirmación**: el flujo puede requerir validación del cliente o confirmar automáticamente según configuración.

## Vistas modificadas

- **Formulario de contactos** (`base.view_partner_form`): añade `whatsapp_phone` y `whatsapp_order_enabled` a continuación del campo `category_id` (etiquetas), usando el XPath `//field[@name='category_id']` con `position="after"`.
- **Ajustes de ventas** (`sale.res_config_settings_view_form`): añade bloque de configuración de Meta, OpenAI, límites y comportamiento.
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
        └── Technical_context.md
```

## Instalación / Actualización

```bash
cd /opt/odoo18_desarrollo/odoo
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev -i klo_whatsapp_order --stop-after-init

/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev -u klo_whatsapp_order --stop-after-init
```

## Posibles adaptaciones futuras

- **Multiempresa**: parametrizar credenciales Meta/OpenAI por compañía.
- **Rate limiting**: añadir límites por partner, por número y por ventana temporal.
- **Fallback humano**: derivar sesiones dudosas a un comercial o cola de soporte.
- **RGPD**: anonimización, retención limitada del histórico y consentimiento explícito del canal.
