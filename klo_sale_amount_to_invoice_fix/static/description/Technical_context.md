# KLO — Fix amount_to_invoice para líneas con qty=0

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_sale_amount_to_invoice_fix`           |
| Nombre legible   | KLO - Fix amount_to_invoice para líneas con qty=0 |
| Versión          | `18.0.1.0.0`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | Sales                                      |
| Dependencias     | `sale`                                     |
| Ubicación        | `extra-addons/klo/extra/klo_sale_amount_to_invoice_fix` |
| Fecha creación   | 2026-07-21                                 |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

Corrige el campo `amount_to_invoice` del pedido de venta (`sale.order`) para líneas
de pedido que tienen `product_uom_qty = 0` pero que han sido facturadas
(`qty_invoiced_posted > 0`).

Este caso se produce cuando:
- Se añaden líneas como palets con cantidad 0 al pedido y se facturan directamente.
- Se modifican líneas para registrar devoluciones, incrementando `qty_invoiced`
  por encima de `product_uom_qty`.

El método estándar de Odoo `_compute_amount_to_invoice` en `sale.order.line`
devuelve `amount_to_invoice = 0.0` cuando `product_uom_qty = 0`, sin contemplar
que la línea puede tener facturas publicadas. Esto provoca que el campo
`amount_to_invoice` del pedido (`sale.order`) no muestre la diferencia entre
el total del pedido y lo facturado.

---

## Estructura de archivos

```
klo_sale_amount_to_invoice_fix/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line.py
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Modelos afectados

### `sale.order.line` — Línea de pedido de venta

**Archivo:** `models/sale_order_line.py`
**Tipo de herencia:** `_inherit = "sale.order.line"`

#### Campos añadidos / modificados

No añade campos. Sobrescribe el método de cálculo de un campo existente.

#### Métodos sobreescritos

```python
@api.depends('discount', 'price_total', 'product_uom_qty', 'qty_delivered', 'qty_invoiced_posted')
def _compute_amount_to_invoice(self):
```

Llama al método estándar con `super()` y posteriormente ajusta las líneas donde
`product_uom_qty = 0` y `qty_invoiced_posted > 0`. Para estas líneas, calcula
`amount_to_invoice` a partir de las líneas de factura publicadas (`invoice_lines`).

**Lógica del ajuste:**
1. Se obtienen las líneas de factura publicadas via `_get_invoice_lines()`.
2. Se suma `price_total * -direction_sign` de cada línea de factura para obtener
   el importe total facturado (con signo correcto: positivo para facturas,
   negativo para abonos).
3. Se calcula el precio unitario total (impuestos incluidos) dividiendo entre
   `qty_invoiced_posted`.
4. Se calcula `qty_to_invoice = uom_qty_to_consider - qty_invoiced_posted`.
5. Se asigna `amount_to_invoice = unit_price_total * qty_to_invoice`.

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Línea con product_uom_qty > 0, totalmente facturada | amount_to_invoice = 0 (sin cambios, comportamiento estándar) |
| Línea con product_uom_qty > 0, parcialmente facturada | amount_to_invoice = diferencia (sin cambios, comportamiento estándar) |
| Línea con product_uom_qty = 0, qty_invoiced_posted = 0 | amount_to_invoice = 0 (sin cambios) |
| Línea con product_uom_qty = 0, qty_invoiced_posted > 0 (factura) | amount_to_invoice = -price_total_unitario * qty_invoiced_posted (AJUSTE) |
| Línea con product_uom_qty = 0, qty_invoiced_posted < 0 (abono) | amount_to_invoice = -price_total_unitario * qty_invoiced_posted (AJUSTE) |

### Ejemplo real: Pedido V26002031

Línea 7878 (PALETS MADERA CMIRA 100):
- product_uom_qty = 0, qty_delivered = 0, qty_invoiced = 1
- qty_to_invoice = -1, untaxed_amount_to_invoice = -6.00
- **Sin fix:** amount_to_invoice = 0.0 (INCORRECTO)
- **Con fix:** amount_to_invoice = -7.26 (CORRECTO: precio unitario con impuestos * qty negativa)

---

## Notas para IA / desarrollador

- **Campo clave:** `sale.order.amount_to_invoice` — Suma de `amount_to_invoice` de todas las líneas del pedido. Usado para el saldo no facturado.
- **Campo clave:** `sale.order.line.amount_to_invoice` — Calculado por `_compute_amount_to_invoice`. Usa `price_total` (impuestos incluidos) y `qty_invoiced_posted`.
- **Campo relacionado:** `sale.order.line.untaxed_amount_to_invoice` — Calculado por `_compute_untaxed_amount_to_invoice`. Usa `untaxed_amount_invoiced` (base imponible). Ya funciona correctamente para líneas con product_uom_qty=0.
- **Método clave:** `_get_invoice_lines()` en `sale.order.line` — Devuelve las líneas de factura vinculadas a la línea de pedido.
- **Dependencias de triggers:** `qty_invoiced_posted` depende de `invoice_lines.move_id.state` e `invoice_lines.quantity`. Cualquier cambio en las líneas de factura recalcula `qty_invoiced_posted`, que a su vez dispara `_compute_amount_to_invoice`.
- **Casos borde:** El fix solo actúa cuando `product_uom_qty = 0` Y `qty_invoiced_posted != 0`. Para el resto de líneas, el comportamiento es el estándar de Odoo.

---

## Instalación y actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d ryp_dev \
    -u klo_sale_amount_to_invoice_fix \
    --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-07-21 | Versión inicial — Fix para líneas con product_uom_qty=0 facturadas |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
