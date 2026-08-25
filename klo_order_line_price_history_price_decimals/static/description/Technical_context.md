# Technical Context — `klo_order_line_price_history_price_decimals`

## Módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_order_line_price_history_price_decimals` |
| **Nombre legible** | KLO - Order Line Price History Price Decimals |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales |
| **Dependencias** | `sale_order_line_price_history` (OCA), `purchase` (core) |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_order_line_price_history_price_decimals/` |
| **Odoo versión** | 18.0 Community |

---

## Descripción

Este módulo unifica el arreglo de los decimales del **historial de precios** de líneas de pedido en VENTAS y COMPRAS, de modo que la columna `price_unit` muestre la precisión **"Product Price"** (Ajustes → Técnico → Precisión decimal) en ambos sitios, en lugar de los 2 decimales por defecto del frontend.

- **Ventas:** al pulsar el botón **"Historial de precios"** en una línea de pedido de venta (vista `sale_order_line_price_history.sale_order_line_price_history_view_form`), la columna `price_unit` del wizard mostraba 2 decimales.
- **Compras:** al pulsar **"Historial de precios"** en una línea de pedido de compra (vista `purchase.purchase_history_tree`), la columna `price_unit` también mostraba 2 decimales.

Ambos puntos comparten la misma causa de fondo (el frontend ignora la precisión "Product Price") pero requieren técnicas distintas porque el origen del problema es distinto en cada caso (ver sección *Campo(s) / vista(s) modificadas*).

---

## Campo(s) / vista(s) modificadas

### VENTAS — modelo `sale.order.line.price.history.line`

**Archivo:** `models/sale_order_line_price_history_line.py`
**Tipo de herencia:** `_inherit` (extensión de modelo transient existente del módulo OCA)

| Campo | Tipo | String | Comportamiento |
|-------|------|--------|----------------|
| `price_unit` | `Float` (related) | `Unit Price` (heredado) | Se sobrescribe añadiendo `min_display_digits="Product Price"` para que el frontend respete la precisión "Product Price" en la vista lista y en el form del wizard |

Definición del campo:

```python
price_unit = fields.Float(
    related="sale_order_line_id.price_unit",
    min_display_digits="Product Price",
)
```

**Causa raíz (ventas):**

- El módulo OCA `sale_order_line_price_history` define en `wizards/sale_order_line_price_history.py` el modelo transient `sale.order.line.price.history.line` con:
  ```python
  price_unit = fields.Float(related="sale_order_line_id.price_unit")
  ```
  sin `digits` ni `min_display_digits`.
- En Odoo 18, `sale.order.line.price_unit` usa `min_display_digits='Product Price'` (NO usa `digits`).
- Los campos `related` heredan `digits` pero **NO** heredan `min_display_digits` (no existe `_related__min_display_digits` en `odoo/fields.py`).
- Por eso el related se muestra con 2 decimales (default del frontend) y hay que redeclararlo en el modelo.

> **Nota de diseño:** se usa `min_display_digits` (NO `digits`) para ser fiel al core de Odoo 18 y a la precedencia del proyecto. `min_display_digits` muestra **como mínimo** los decimales configurados en "Product Price"; si el valor tiene más decimales significativos, puede mostrar más, sin truncar.

### COMPRAS — vista `purchase.purchase_history_tree`

**Archivo:** `views/purchase_order_line_views.xml`
**Tipo de herencia:** herencia de vista (`ir.ui.view`, `inherit_id`)

| Campo | Atributo añadido | Comportamiento |
|-------|------------------|----------------|
| `price_unit` | `options="{'field_digits': True}"` | Obliga al widget `monetary` a usar los `digits`/`min_display_digits` del campo en lugar de los decimales de la moneda |

Definición de la vista heredada:

```xml
<record id="klo_purchase_history_tree_price_unit" model="ir.ui.view">
    <field name="name">klo.purchase.history.list.price_unit</field>
    <field name="model">purchase.order.line</field>
    <field name="inherit_id" ref="purchase.purchase_history_tree"/>
    <field name="arch" type="xml">
        <field name="price_unit" position="attributes">
            <attribute name="options">{'field_digits': True}</attribute>
        </field>
    </field>
</record>
```

**Causa raíz (compras):**

- En Odoo 18, `purchase.order.line.price_unit` **YA** usa `min_display_digits='Product Price'` (el modelo está correcto, no se toca).
- El problema es que la vista `purchase.purchase_history_tree` renderiza `price_unit` con `widget="monetary"`.
- El widget `monetary` formatea el valor con los **decimales de la MONEDA** (típicamente 2), ignorando la precisión del campo.
- La solución idiomática en Odoo 18 es añadir `options="{'field_digits': True}"` al campo (manteniendo `widget="monetary"` y el símbolo de moneda). Esto hace que el widget use los `digits`/`min_display_digits` del campo. Es el mismo patrón usado en `odoo/addons/product/views/product_views.xml`, `product_attribute_views.xml`, etc.
- Por eso aquí el fix es **solo de vista** y no de modelo.

### Diferencia entre los dos fixes

| Aspecto | Ventas | Compras |
|---|---|---|
| Origen del problema | El campo related del transient NO hereda `min_display_digits` | El widget `monetary` ignora la precisión del campo |
| Dónde se arregla | Modelo (redeclarar campo) | Vista (añadir `options`) |
| Por qué no sirve el otro fix | No hay vista que heredar con `field_digits` porque el campo del transient no tiene `min_display_digits` que leer | No hay modelo que tocar: `purchase.order.line.price_unit` ya tiene `min_display_digits='Product Price'` |

---

## Dependencias

| Módulo | Propósito | Ruta |
|---|---|---|
| `sale_order_line_price_history` (OCA, sale-workflow) | Provee el modelo transient `sale.order.line.price.history.line` cuyo campo `price_unit` se sobrescribe | `/opt/odoo18_desarrollo/extra-addons/oca/sale-workflow/sale_order_line_price_history/` |
| `purchase` (core Odoo) | Provee la vista `purchase.purchase_history_tree` (modelo `purchase.order.line`) que se hereda | `odoo/addons/purchase/` |

No depende de otros módulos `klo_*`.

---

## Lógica

No hay métodos sobreescritos ni `compute`/`onchange`/triggers. La lógica es puramente declarativa:

1. **Ventas (modelo):** se hereda el transient `sale.order.line.price.history.line` vía `_inherit` y se redeclara `price_unit` manteniendo el `related="sale_order_line_id.price_unit"` original y añadiendo `min_display_digits="Product Price"`. Al redeclarar un campo con el mismo nombre en un `_inherit`, Odoo fusiona los atributos: el `related` se conserva y se añade `min_display_digits`.
2. **Compras (vista):** se hereda `purchase.purchase_history_tree` y se añade `options="{'field_digits': True}"` al campo `price_unit` mediante `position="attributes"`. El frontend (`formatters.js`/`numbers.js` y el widget `monetary`) respeta `field_digits` y usa la precisión del campo.

No se crea ningún registro en `decimal.precision`: la precisión "Product Price" ya existe en Odoo base.

---

## Vistas modificadas

| Vista heredada | Registro | Cambio |
|---|---|---|
| `purchase.purchase_history_tree` (modelo `purchase.order.line`) | `klo_purchase_history_tree_price_unit` | Se añade `options="{'field_digits': True}"` al campo `price_unit` (manteniendo `widget="monetary"`) |

La vista de ventas **no se modifica**: el frontend aplica `min_display_digits` automáticamente a partir de la definición del campo en el modelo.

---

## Estructura de archivos

```
klo_order_line_price_history_price_decimals/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line_price_history_line.py   ← Sobrescribe price_unit con min_display_digits (ventas)
├── views/
│   └── purchase_order_line_views.xml            ← Añade options={'field_digits': True} a price_unit (compras)
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md                 ← Este fichero
```

> No hay directorio `security/`, `data/` ni `demo/` (no son necesarios). Tampoco `views/__init__.py` (no se requiere en Odoo para vistas XML).

---

## Instalación / Actualización

La base de datos activa se lee de `db_name` en `/opt/odoo18_desarrollo/config/odoo.conf` (no hardcodificarla).

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <nombre_base_datos> -i klo_order_line_price_history_price_decimals --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <nombre_base_datos> -u klo_order_line_price_history_price_decimals --stop-after-init
```

Alternativa con uv:

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> -u klo_order_line_price_history_price_decimals --stop-after-init
```

---

## Posibles adaptaciones futuras

- **Contribuir ambos fixes upstream:**
  - El `min_display_digits='Product Price'` en el related del transient de `sale_order_line_price_history` (OCA). Si se aceptara upstream, la parte de ventas de este módulo KLO podría quedar obsoleta.
  - El `options="{'field_digits': True}"` en `purchase.purchase_history_tree` (core Odoo). Si se aceptara upstream, la parte de compras de este módulo KLO podría quedar obsoleta.
- **Aplicar la misma técnica a otros campos related del wizard de ventas:** `product_uom_qty` y `discount` también se definen como `related` sin `min_display_digits` en el módulo OCA. Si se requiriera precisión consistente en esos campos, podrían sobrescribirse de forma análoga (p. ej. `discount` con `min_display_digits="Discount"`).
- **Aplicar `field_digits` a otros widgets `monetary`** del historial de compras/ventas si se detectan más columnas con el mismo problema de precisión.
- **Migración a `digits` si se exige truncado exacto:** si en el futuro se quisiera forzar exactamente N decimales (truncando), se podría sustituir `min_display_digits` por `digits=dp.get_precision("Product Price")`. No es lo recomendado por el proyecto (precedencia: `min_display_digits`).
