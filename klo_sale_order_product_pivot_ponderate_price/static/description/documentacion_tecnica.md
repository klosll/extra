# Documentación Técnica — klo_sale_order_product_pivot_ponderate_price

## Información general

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_sale_order_product_pivot_ponderate_price` |
| **Versión** | 14.0.1.0.0 |
| **Módulo base** | `sale` |
| **Ubicación** | `/opt/odoo14_paasa/extra-addons/extra/klo_sale_order_product_pivot_ponderate_price/` |
| **Autor** | KLO |
| **Fecha creación** | 2026-05-19 |

---

## Objetivo

Añadir una nueva medida calculada **"P. ponderado uni."** (`precio_ponderado_unitario`) al informe pivot de Análisis de Ventas (`sale.view_order_product_pivot`, modelo `sale.report`).

### Fórmula

```
P. ponderado uni. = Base imponible (price_subtotal) / Cantidad enviada (qty_delivered)
```

Si `qty_delivered = 0`, el resultado es `0` para evitar división por cero.

---

## Estructura del módulo

```
klo_sale_order_product_pivot_ponderate_price/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_report.py             ← campo + SQL calculado
├── views/
│   └── sale_report_views.xml      ← herencia de la vista pivot
└── static/description/
    ├── icon.png
    └── documentacion_tecnica.md   ← este fichero
```

---

## Modelo: `sale.report` (herencia)

### Nuevo campo

| Propiedad | Valor |
|---|---|
| **Nombre técnico** | `precio_ponderado_unitario` |
| **Etiqueta** | `P. ponderado uni.` |
| **Tipo** | `Float` (16,4) |
| **Readonly** | Sí |
| **group_operator** | `'sum'` (predeterminado para Float; necesario para que el pivot JS lo reconozca como medida válida) |

### Método sobreescrito: `_select_additional_fields`

Se usa el hook oficial del modelo `sale.report` para inyectar la columna SQL en el `SELECT` de la vista de base de datos.

La columna SQL añadida calcula el precio ponderado **por fila** (por combinación `product_id + order_id`):

```sql
CASE
    WHEN l.product_id IS NOT NULL
         AND sum(l.qty_delivered / u.factor * u2.factor) != 0
    THEN
        sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0)
            WHEN 0 THEN 1.0 ELSE s.currency_rate END)
        /
        sum(l.qty_delivered / u.factor * u2.factor)
    ELSE 0
END as precio_ponderado_unitario
```

Los ajustes de conversión de UdM (`u.factor * u2.factor`) y de moneda (`currency_rate`) son consistentes con el resto de campos del modelo base.

### Método sobreescrito: `init`

Regenera la vista SQL de la base de datos al instalar/actualizar el módulo para incluir la nueva columna.

### Método sobreescrito: `read_group`

**Clave del módulo**: garantiza que en cualquier agrupación del pivot el valor mostrado sea siempre:

```
precio_ponderado_unitario = SUM(price_subtotal) / SUM(qty_delivered)
```

#### Bug crítico corregido — formato `campo:operador`

El pivot JavaScript de Odoo (fichero `pivot_model.js`, función `_getMeasureSpecs`) envía las medidas en formato `'campo:operador'` al backend Python. Por tanto, el backend recibe `'precio_ponderado_unitario:sum'` en lugar de `'precio_ponderado_unitario'`. Sin esta corrección, el `read_group` override nunca detectaba el campo y siempre devolvía la suma directa.

La detección correcta:
```python
needs_calc = any(
    f == 'precio_ponderado_unitario' or f.startswith('precio_ponderado_unitario:')
    for f in fields
)
```

#### Flujo de ejecución completo

1. El pivot JS llama `read_group` con `fields=['precio_ponderado_unitario:sum', ...]`
2. Nuestro override detecta `'precio_ponderado_unitario:sum'` como el campo a calcular
3. Excluye `precio_ponderado_unitario` (en cualquier formato) de la query al super
4. Añade `price_subtotal` y `qty_delivered` si no estaban ya en la lista
5. `super().read_group()` ejecuta: `SUM(price_subtotal)`, `SUM(qty_delivered)` GROUP BY ...
6. Para cada grupo: `precio_ponderado_unitario = round(SUM(price_subtotal) / SUM(qty_delivered), 4)`
7. Elimina `price_subtotal` y `qty_delivered` del resultado si se añadieron solo para el cálculo

> **Nota**: `group_operator='sum'` es necesario para que el pivot JS reconozca el campo como medida válida. Sin él, el JS lanza `Error: No aggregate function has been provided for the measure`.

---

## Vista: herencia de `sale.view_order_product_pivot`

Se añade la nueva medida **después** del campo `price_subtotal`:

```xml
<field name="precio_ponderado_unitario" type="measure" string="P. ponderado uni."/>
```

---

## Comportamiento en el pivot

- La medida aparece en el selector de medidas del pivot de **Ventas → Análisis de ventas**.
- **En cualquier nivel de agrupación** (por equipo, fecha, producto, etc.), el valor mostrado es siempre `SUM(price_subtotal) / SUM(qty_delivered)` del grupo, gracias al `read_group` sobreescrito.
- Si `qty_delivered = 0` en el grupo, el valor es `0.0` para evitar división por cero.
- El valor se redondea a 4 decimales.

---

## Instalación

1. Ir a **Aplicaciones** → Actualizar lista
2. Buscar `KLO Ventas - Precio ponderado unitario en pivot`
3. Instalar

---

## Notas de mantenimiento

- Si se actualiza el método `_query()` o `_select_sale()` del modelo base `sale.report`, revisar que los alias de las columnas SQL (`u.factor`, `u2.factor`, `s.currency_rate`) sigan siendo válidos.
- El módulo depende únicamente de `sale`. No requiere módulos adicionales.

