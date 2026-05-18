# Technical Document — `klo_saleorder_sended_signed_states`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_saleorder_sended_signed_states` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_saleorder_sended_signed_states/` |

---

## Descripción

Añade dos columnas opcionales (visibles por defecto) en la lista de pedidos de venta (`sale.sale_order_tree`):

### Campo 1: `is_email_sent` — "Enviado"
- **Tipo:** `Boolean` (almacenado, `copy=False`, `tracking=True`)
- **Descripción:** Indica si el pedido ha sido enviado por correo electrónico al menos una vez, independientemente del estado actual (`state`). A diferencia del estado "Presupuesto enviado", este campo **no se resetea** al confirmar el pedido.
- **Se activa en:** Override de `action_quotation_sent()` → `write({'is_email_sent': True})`

### Campo 2: `delivery_signed_status` — "Entregas firmadas"
- **Tipo:** `Selection` (calculado y almacenado)
- **Valores:**
  - `no` → "No" (rojo)
  - `partial` → "Parcialmente" (naranja)
  - `yes` → "Sí" (verde)
- **Descripción:** Estado de firma de las entregas de salida al cliente (`location_dest_id.usage == 'customer'`) en estado `done`.
- **Depende de:** `picking_ids.state`, `picking_ids.is_signed`, `picking_ids.location_dest_id.usage`

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale_stock` | Relación `picking_ids` en `sale.order` + `stock.picking` con campos `is_signed` y `signature` |

---

## Estructura de archivos

```
klo_saleorder_sended_signed_states/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order.py
├── views/
│   └── sale_order_view.xml
└── static/description/
    ├── icon.png
    └── Tecnical_document.md
```

---

## Lógica de cálculo — `delivery_signed_status`

```python
done_deliveries = picking_ids.filtered(
    state == 'done' AND location_dest_id.usage == 'customer'
)

if not done_deliveries:       → 'no'
elif all signed:              → 'yes'
elif some signed:             → 'partial'
else:                         → 'no'
```

---

## Vista heredada

- **Hereda:** `sale.sale_order_tree`
- **Posición:** Después de `invoice_status`
- `is_email_sent`: `widget="boolean"`, `optional="show"`, `readonly="1"`
- `delivery_signed_status`: `widget="badge"` con colores semáforo, `optional="show"`, `readonly="1"`

---

## Instalación / Actualización

```bash
# Instalar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/odoo/config/odoo.conf \
  -d ryp_dev -i klo_saleorder_sended_signed_states \
  --stop-after-init --no-http

# Actualizar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/odoo/config/odoo.conf \
  -d ryp_dev -u klo_saleorder_sended_signed_states \
  --stop-after-init --no-http
```

---

## Posibles adaptaciones futuras

- **Retroactivo "Enviado":** Para marcar pedidos históricos ya enviados, se puede crear un script de migración que busque mensajes de tipo `email` en `mail.message` sobre `sale.order` y establezca `is_email_sent = True`.
- **Entregas internas:** Ampliar `delivery_signed_status` para incluir también albaranes de otros tipos si es necesario.
- **Campo en formulario:** Añadir `is_email_sent` como campo visible (readonly) en el formulario del pedido de venta.

