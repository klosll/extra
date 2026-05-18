# Technical Document — `klo_saleorder_project_by_partner`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_saleorder_project_by_partner` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_saleorder_project_by_partner/` |

---

## Descripción

En el formulario de pedido de venta (`sale.order`), el campo **Proyecto** (`project_id`) se filtra automáticamente para mostrar únicamente los proyectos asignados al cliente del pedido (`partner_id`). También se muestran proyectos sin cliente asignado (proyectos genéricos, `partner_id = False`).

El campo se posiciona **debajo del campo Modo de pago** (`payment_mode_id`), en lugar de la posición original definida por `sale_project` (antes de `journal_id`).

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale_project` | Define el campo `project_id` en `sale.order` con dominio `allow_billable = True` |
| `account_payment_sale` | Define el campo `payment_mode_id` en `sale.order` (OCA bank-payment) |

---

## Estructura de archivos

```
klo_saleorder_project_by_partner/
├── __init__.py
├── __manifest__.py
├── views/
│   └── sale_order_view.xml
└── static/description/
    ├── icon.png
    └── Tecnical_document.md
```

---

## Vistas heredadas

### Vista 1: `klo.sale.order.form.project.by.partner`
- **Hereda:** `sale_project.view_order_form_inherit_sale_project`
- **Acción:** Oculta el `project_id` de la posición original (antes de `journal_id`) usando `invisible=1`

### Vista 2: `klo.sale.order.form.project.after.payment.mode`
- **Hereda:** `sale.view_order_form`
- **Acción:** Añade el campo `project_id` después de `payment_mode_id` con:
  - `domain="[('allow_billable', '=', True), ('partner_id', 'in', [partner_id, False])]"`
  - `context="{'default_allow_billable': True, 'default_partner_id': partner_id}"`
  - `groups="project.group_project_user"`

---

## Lógica del dominio

```python
[
    ('allow_billable', '=', True),           # Solo proyectos facturables (hereda dominio original)
    ('partner_id', 'in', [partner_id, False]) # Proyectos del cliente O sin cliente asignado
]
```

- `partner_id` en el dominio hace referencia al valor actual del campo `partner_id` del pedido de venta.
- El `False` en el `in` permite mostrar proyectos genéricos (sin cliente específico).

---

## Comportamiento

| Situación | Resultado |
|---|---|
| Pedido sin cliente asignado | Muestra todos los proyectos con `allow_billable = True` y sin cliente |
| Pedido con cliente A | Muestra proyectos del cliente A + proyectos sin cliente |
| Pedido con cliente B | Muestra proyectos del cliente B + proyectos sin cliente |
| Crear proyecto desde el campo | `default_allow_billable = True` y `default_partner_id = partner_id` del pedido |

---

## Instalación / Actualización

```bash
# Instalar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/odoo/config/odoo.conf \
  -d ryp_dev -i klo_saleorder_project_by_partner \
  --stop-after-init --no-http

# Actualizar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/odoo/config/odoo.conf \
  -d ryp_dev -u klo_saleorder_project_by_partner \
  --stop-after-init --no-http
```

---

## Posibles adaptaciones futuras

- **Sin `account_payment_sale`:** Si el módulo OCA no está instalado, separar en dos dependencias opcionales y posicionar `project_id` después de `payment_term_id` como fallback.
- **Filtro por almacén:** Añadir filtro adicional por `company_id` si hay entornos multicompañía.
- **Filtro estricto:** Eliminar el `False` del dominio si se quiere forzar que solo aparezcan proyectos del cliente (sin proyectos genéricos).

