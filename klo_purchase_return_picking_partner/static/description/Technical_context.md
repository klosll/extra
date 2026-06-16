# KLO — klo_purchase_return_picking_partner

> **Documento técnico del módulo.**
> Orientado a ser procesado por una IA para futuros ajustes y desarrollos.

---

## Identificación del módulo

| Campo          | Valor                                                                           |
|----------------|---------------------------------------------------------------------------------|
| Nombre técnico | `klo_purchase_return_picking_partner`                                           |
| Nombre legible | KLO - Purchase Return Picking Partner                                           |
| Versión        | `18.0.1.0.0`                                                                    |
| Autor          | KLO Ingeniería Informática S.L.L.                                               |
| Licencia       | AGPL-3                                                                          |
| Categoría      | `Purchase/Purchase`                                                             |
| Dependencias   | `purchase_stock`                                                                |
| Ubicación      | `extra-addons/klo/extra/klo_purchase_return_picking_partner`                   |
| Fecha creación | `2026-06-16`                                                                    |
| Odoo versión   | 18.0 Community                                                                  |

---

## Descripción funcional

Corrige un bug de Odoo 18 en el módulo `purchase_stock` que provoca que el albarán
generado al confirmar un pedido de compra con **cantidades negativas** (devolución al
proveedor) quede sin `partner_id` (Dirección de entrega/proveedor vacía).

### Síntoma

Al confirmar (`button_confirm`) un pedido de compra con alguna línea con cantidad
negativa (p.ej. `-3` unidades), Odoo crea un albarán de tipo "Órdenes de entrega"
(devolución al proveedor) con el campo `partner_id` vacío. En cambio, pedidos con
cantidades positivas generan recepciones con el proveedor correctamente asignado.

---

## Causa raíz

El flujo estándar de Odoo para pedidos con cantidades **positivas**:

1. `_create_picking()` → `_prepare_picking()` crea el albarán de recepción con
   `partner_id = order.partner_id`.
2. El movimiento de stock se crea con `partner_id = dest_address_id.id`
   (vacío en POs normales, solo relleno en dropship).
3. El movimiento queda en el mismo albarán → el albarán conserva su `partner_id`.

El flujo para cantidades **negativas** diverge en `stock.move._action_confirm()`:

1. Los movimientos con `product_uom_qty < 0` son identificados como `neg_r_moves`.
2. Odoo invierte `location_id` / `location_dest_id` y multiplica la cantidad por `-1`.
3. Cambia `picking_type_id` al tipo de **retorno** (`return_picking_type_id`), p.ej.
   de "Recepciones" a "Órdenes de entrega".
4. Llama `neg_r_moves._assign_picking()` directamente.
5. `_assign_picking()` no encuentra el albarán original (tipo diferente) y crea uno
   nuevo con `_get_new_picking_values()`.
6. `_get_new_picking_values()` obtiene `partner_id` de `self.mapped('partner_id')`
   sobre los movimientos, que es `False` (ya que `dest_address_id` está vacío en POs
   normales).
7. El nuevo albarán de devolución se crea **sin proveedor**.

El albarán inicial creado por `_prepare_picking()` (con `partner_id` correcto) queda
huérfano sin movimientos.

---

## Solución implementada

Se extiende `purchase.order.line._prepare_stock_move_vals()` para propagar el
`partner_id` del pedido de compra al campo `partner_id` del movimiento de stock,
cuando no hay `dest_address_id` definido (es decir, en pedidos normales, no dropship).

```python
def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
    vals = super()._prepare_stock_move_vals(...)
    if not vals.get("partner_id") and self.order_id.partner_id:
        vals["partner_id"] = self.order_id.partner_id.id
    return vals
```

Cuando `_get_new_picking_values()` recupera `self.mapped('partner_id')` del movimiento,
ahora obtiene el proveedor del pedido → el albarán de devolución hereda el `partner_id`
correcto.

**Efecto colateral nulo en recepciones positivas**: el albarán de recepción normal
ya se crea con `partner_id` vía `_prepare_picking()` y no pasa por
`_get_new_picking_values()`.

---

## Modelos afectados

### `purchase.order.line` — override de `_prepare_stock_move_vals`

**Archivo:** `models/purchase_order_line.py`
**Tipo de herencia:** `_inherit`

#### Métodos sobreescritos

| Método                    | Dónde se llama                     | Qué añade                                             |
|---------------------------|------------------------------------|-------------------------------------------------------|
| `_prepare_stock_moves`    | `purchase_order_line._create_stock_moves` | Rellena `partner_id` en los vals del movimiento cuando `dest_address_id` está vacío |

---

## Dependencias técnicas

| Módulo         | Propósito                                                      |
|----------------|----------------------------------------------------------------|
| `purchase_stock` | Provee `_prepare_stock_move_vals` que este módulo extiende  |

Código relevante de Odoo core:
- `odoo/addons/purchase_stock/models/purchase_order_line.py` → `_prepare_stock_move_vals`
- `odoo/addons/stock/models/stock_move.py` → `_action_confirm` (líneas 1567-1594), `_assign_picking`, `_get_new_picking_values`

---

## Comportamiento esperado tras la corrección

| Situación                                     | Antes del fix             | Después del fix                 |
|-----------------------------------------------|---------------------------|---------------------------------|
| PO con qty positiva, confirmar                | Recepción con partner ✓   | Recepción con partner ✓         |
| PO con qty negativa, confirmar                | Entrega sin partner ✗     | Entrega con partner ✓           |
| PO dropship (dest_address_id relleno)         | Dropship con partner ✓    | Dropship con partner ✓ (sin cambios) |

---

## Estructura de archivos

```
klo_purchase_return_picking_partner/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── purchase_order_line.py   ← override de _prepare_stock_move_vals
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md  ← este fichero
```

---

## Instalación y actualización

```bash
# Instalar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev \
    -i klo_purchase_return_picking_partner \
    --stop-after-init

# Actualizar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev \
    -u klo_purchase_return_picking_partner \
    --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio                                                 |
|------------|------------|------------------------------------------------------------------------|
| 18.0.1.0.0 | 2026-06-16 | Versión inicial — fix partner_id en albarán de retorno por qty negativa |

---

## Notas para IA / desarrollador

- **Método clave**: `_prepare_stock_move_vals` en `purchase.order.line` — añade el
  `partner_id` del pedido de compra a los valores del movimiento de stock.
- **Flujo clave en stock**: `stock.move._action_confirm()` líneas 1567-1594 en
  `odoo/addons/stock/models/stock_move.py` — aquí Odoo transforma movimientos negativos
  en devoluciones y llama `_assign_picking()`.
- **`_get_new_picking_values()`** en `stock.move` — crea el nuevo albarán a partir de
  `self.mapped('partner_id')`; este es el punto que recibe el valor del fix.
- **No afecta a dropship**: la condición `if not vals.get("partner_id")` preserva el
  `dest_address_id` cuando está definido.
- **Posible extensión**: si se necesita que también funcione en otros escenarios donde
  `dest_address_id` está relleno pero el partner del picking deba ser el proveedor,
  revisar la condición de guarda.

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)

