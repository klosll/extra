# KLO — Stock Picking Report Price Unit Untaxed

> **Documento técnico del módulo `klo_stock_picking_report_price_unit_untaxed`.**
> Elaborado a partir de la plantilla `klo/_templates/static/description/Tecnical_document.md`.
> Orientado a ser procesado por una IA para futuros ajustes y desarrollos.

---

## Módulo

| Campo          | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| name           | `klo_stock_picking_report_price_unit_untaxed`                        |
| version        | `18.0.1.0.0`                                                         |
| author         | KLO Ingeniería Informática S.L.L.                                    |
| license        | AGPL-3                                                               |
| path           | `extra-addons/klo/extra/klo_stock_picking_report_price_unit_untaxed` |
| Nombre legible | KLO - Stock Picking Report Price Unit Untaxed                        |
| Categoría      | Accounting/Accounting                                                |
| Dependencias   | `stock_picking_report_valued`, `klo_sale_order_price_unit_untaxed`   |
| Fecha creación | 2026-10-30                                                           |
| Odoo versión   | 18.0 Community                                                       |

---

## Descripción

Módulo de adaptación que sustituye el precio unitario mostrado en la columna
**Unit Price** del informe de albarán de entrega valorado, mostrando el precio
**sin impuestos** en lugar del precio unitario de venta del OCA
(`sale_price_unit`).

El informe de albarán del core (`stock.report_delivery_document`) no muestra
precios. Las columnas de valoración las aporta el módulo OCA
`stock_picking_report_valued`, que añade Unit Price, Discount, Subtotal y Taxes
dentro de la tabla de líneas de movimiento cuando el albarán es saliente,
está valorado y proviene de un pedido de venta.

Este módulo reutiliza la estructura de columnas del OCA y solo cambia el valor
renderizado en la celda de precio unitario, dejando descuento, subtotal e
impuestos intactos.

---

## Campo(s) añadido(s)

**Modelo:** `stock.move.line` — herencia `_inherit`
**Archivo:** `models/stock_move_line.py`

| Campo | Tipo | String | Descripción |
|-------|------|--------|-------------|
| `price_unit_untaxed` | `Float` | `Precio unitario (sin impuestos)` | Precio unitario sin impuestos de la línea de albarán. No almacenado (`store=False`), `min_display_digits='Product Price'`, calculado al vuelo en el render del informe. |

---

## Dependencias

- `stock_picking_report_valued` (OCA):
  - Ruta: `extra-addons/oca/stock-logistics-reporting/stock_picking_report_valued/`
  - Añade las columnas de valoración al informe de albarán y los campos
    `sale_line`, `sale_price_unit`, `sale_discount`, `sale_price_subtotal` y
    `sale_tax_description` sobre `stock.move.line`.
- `klo_sale_order_price_unit_untaxed` (KLO):
  - Ruta: `extra-addons/klo/extra/klo_sale_order_price_unit_untaxed/`
  - Aporta el campo `price_unit_untaxed` en `sale.order.line` (precio unitario
    sin impuestos y sin redondeo), que es la base del cálculo de este módulo.

---

## Lógica

### Método añadido: `_compute_price_unit_untaxed` (`stock.move.line`)

```python
@api.depends('sale_line', 'product_uom_id', 'sale_line.price_unit_untaxed')
def _compute_price_unit_untaxed(self):
    for line in self:
        if not line.sale_line:
            line.price_unit_untaxed = 0.0
            continue
        line.price_unit_untaxed = line.sale_line.product_uom._compute_price(
            line.sale_line.price_unit_untaxed, line.product_uom_id)
```

- Si la línea de movimiento no está vinculada a una línea de pedido de venta,
  el campo vale `0.0`.
- En caso contrario, se convierte el `price_unit_untaxed` de la línea de venta
  a la unidad de medida de la línea de albarán (`product_uom_id`) usando
  `product.uom._compute_price`.

> **Aclaración sobre el descuento:** el campo `price_unit_untaxed` muestra el
> precio unitario sin impuestos **antes** del descuento; el descuento se sigue
> mostrando en su propia columna y el Neto (descuento aplicado) se calcula e
> incluye en el módulo que consume este campo, igual que en pedido y factura.

**Conversión de unidad de medida:** se utiliza exactamente el mismo mecanismo
que emplea el OCA para calcular `sale_price_unit`:

```python
line.sale_line.product_uom._compute_price(
    line.sale_line.price_unit, line.product_uom_id)
```

De este modo, el precio con impuestos (`sale_price_unit`) y el precio sin
impuestos (`price_unit_untaxed`) son comparables en la misma unidad de medida.

**Fuente del valor base:** el campo `price_unit_untaxed` de `sale.order.line`
es aportado por `klo_sale_order_price_unit_untaxed` y contiene el precio
unitario sin redondeo y sin impuestos.

**Formato de visualización:** `min_display_digits='Product Price'` imita el
campo `price_unit` del core. Al renderizar con `t-field`, se muestran los
mismos decimales que en el formulario y no se añade símbolo de moneda.

---

## Vistas modificadas

### `stock.stock_report_delivery_has_serial_move_line` — Celdas de líneas de albarán valoradas

**Archivo:** `report/stock_picking_report_templates.xml`
**ID template:** `klo_stock_picking_price_unit_untaxed`
**Hereda:** `stock.stock_report_delivery_has_serial_move_line`
**Prioridad:** `18` (para aplicarse después del OCA `stock_picking_report_valued`,
que usa `priority="17"`)

#### XPath aplicado

```xml
<xpath expr="//span[@t-field='move_line.sale_price_unit']" position="replace">
    <span t-field="move_line.price_unit_untaxed"/>
</xpath>
```

**Motivo del cambio:** el OCA muestra en la columna "Unit Price" el campo
`move_line.sale_price_unit`, que contiene el precio unitario del pedido de
venta (con impuestos si el producto está configurado como precio incluido).
Se sustituye el `<span>` por uno que renderiza `move_line.price_unit_untaxed`.

**Superficie mínima:** el reemplazo se limita exclusivamente al `<span>`
interior. El `<td>` que lo contiene, sus clases (`text-end`) y el resto de
celdas (descuento, subtotal, impuestos) permanecen intactos. De esta forma se
minimizan las colisiones con otras herencias del mismo template.

**Formato:** el nuevo span usa `t-field` sobre un campo con
`min_display_digits='Product Price'`, por lo que muestra los mismos decimales
que `price_unit` en el formulario y sin símbolo de moneda.

---

## Estructura de archivos

```
klo_stock_picking_report_price_unit_untaxed/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── stock_move_line.py                 # Campo computado price_unit_untaxed
├── report/
│   └── stock_picking_report_templates.xml # Herencia del informe valorado
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Instalación / Actualización

Instalación (primera vez):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <db_name> \
    -i klo_stock_picking_report_price_unit_untaxed \
    --stop-after-init
```

Actualización (tarea de desarrollo habitual):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <db_name> \
    -u klo_stock_picking_report_price_unit_untaxed \
    --stop-after-init
```

> La base de datos activa se define en `db_name` de `config/odoo.conf`; no
> hardcodear el nombre de la base de datos.

---

## Posibles adaptaciones futuras

- Extender el reemplazo a las filas agregadas por el OCA si en el futuro se
  valorizan líneas adicionales o se añaden nuevas celdas con
  `sale_price_unit`. Actualmente solo existe un único span con ese campo en el
  template heredado.
- Si el cliente pidiera mostrar también el precio unitario sin impuestos **con
  descuento aplicado**, se podría añadir un campo adicional
  `price_unit_untaxed_discounted` y un segundo xpath sobre el span del
  descuento o crear una columna nueva.
- Si el OCA añadiera otra fila de totales con `sale_price_unit`, habría que
  revisar la unicidad del xpath para evitar reemplazos múltiples.
- Replicar el patrón en otros documentos de entrega (p. ej. notas de entrega o
  informes de picking personalizados) si fuera necesario.

---

## Datos de configuración

Ninguno. El módulo no carga datos iniciales, secuencias, grupos ni parámetros, y no
incluye datos demo (convención KLO).

---

## Comportamiento esperado

| Situación | Resultado en columna "Unit Price" |
|-----------|-----------------------------------|
| Albarán saliente, valorado y con pedido de venta | Se muestra `price_unit_untaxed` (sin impuestos) |
| Albarán no saliente / no valorado / sin venta | El OCA no muestra las columnas de valoración; el campo no se renderiza |
| Línea de movimiento sin línea de venta | El campo vale `0.0` |
| Producto en unidad de medida diferente a la del pedido | Se convierte el precio a la UdM del movimiento |

---

## Notas para IA / desarrollador

- **Campo clave:** `stock.move.line.price_unit_untaxed` — `Float` no almacenado,
  se calcula al vuelo en el render del informe.
- **Template clave:** `stock.stock_report_delivery_has_serial_move_line` — QWeb
  de las líneas de albarán con serie/lote, heredado por el OCA con
  `priority="17"`.
- **Método clave:** `_compute_price_unit_untaxed` en `stock.move.line` —
  convierte `sale_line.price_unit_untaxed` a la unidad de medida del movimiento.
- **Consideraciones:**
  - El módulo no debe instalarse sin `stock_picking_report_valued` y
    `klo_sale_order_price_unit_untaxed` (declarados en `depends`).
  - La prioridad del template es `18` para garantizar que se aplica después del
    OCA (`priority="17"`).
  - El reemplazo se limita al `<span>` para no romper herencias del OCA ni del
    core sobre el `<td>` o la tabla.
  - Licencia AGPL-3 según la convención vigente de AGENTS.md.

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-30 | Versión inicial: campo computado `price_unit_untaxed`, herencia del template con `priority="18"` y documentación técnica |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
