# Contexto técnico: klo_sale_report_price_unit_decimals

## Descripción del módulo a crear

**Nombre del módulo:** `klo_sale_report_price_unit_decimals`  
**Ubicación:** `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_sale_report_price_unit_decimals/`  
**Versión Odoo:** 18.0 Community  
**Fecha de análisis:** 2026-04-17  

---

## Objetivo

Adaptar la vista de **Análisis de Ventas** (`Ventas → Informes → Ventas`) para que el campo **Precio Unitario** (`price_unit`) se muestre con los decimales configurados en la **Precisión Decimal "Product Price"** de Odoo (`Ajustes → Técnico → Precisión decimal`), tanto en la vista lista como en la vista pivot.

---

## Análisis del estado actual (Odoo 18 base)

### Modelo: `sale.report`
- **Archivo:** `/opt/odoo18_desarrollo/odoo/addons/sale/report/sale_report.py`
- El campo `price_unit` está definido como:
  ```python
  price_unit = fields.Float(string="Unit Price", aggregator='avg', readonly=True)
  ```
- **Problema:** No tiene asignada la precisión decimal `'Product Price'`. Usa el Float genérico (6 decimales por defecto), ignorando la configuración de precisión decimal del sistema.
- En SQL, se calcula como `AVG(l.price_unit / currency_rate * account_currency_rate)`.

### Comparativa con `sale.order.line`
- En `sale.order.line`, `price_unit` sí usa precisión decimal:
  ```python
  price_unit = fields.Float(
      string="Unit Price",
      compute='_compute_price_unit',
      min_display_digits='Product Price',
      store=True, readonly=False, required=True, precompute=True)
  ```
- El parámetro clave es `min_display_digits='Product Price'`.

### Vista lista: `sale_report_view_tree`
- **XML ID:** `sale.sale_report_view_tree`
- **Archivo:** `/opt/odoo18_desarrollo/odoo/addons/sale/report/sale_report_views.xml` (línea 52)
- El campo `price_unit` **ya aparece** en esta vista:
  ```xml
  <field name="price_unit" widget="monetary" avg="Average"/>
  ```
- **Problema:** Al usar `widget="monetary"`, los decimales los controla la moneda (`currency_id`), no la precisión `Product Price`. Si la moneda tiene 2 decimales y el precio tiene más, se trunca.

### Vista pivot: `view_order_product_pivot`
- **XML ID:** `sale.view_order_product_pivot`
- **Archivo:** `/opt/odoo18_desarrollo/odoo/addons/sale/report/sale_report_views.xml` (línea 4)
- El campo `price_unit` **NO aparece** en esta vista. Hay que añadirlo como medida disponible.

---

## Solución propuesta para el módulo `klo_sale_report_price_unit_decimals`

### 1. Herencia del modelo `sale.report`

Sobrescribir el campo `price_unit` añadiendo `min_display_digits='Product Price'`:

```python
# models/sale_report.py
from odoo import fields, models

class SaleReport(models.Model):
    _inherit = 'sale.report'

    price_unit = fields.Float(
        string="Unit Price",
        aggregator='avg',
        readonly=True,
        min_display_digits='Product Price',
    )
```

### 2. Herencia de la vista lista `sale_report_view_tree`

Se elimina el `widget="monetary"` y se deja el campo como Float puro para que respete `min_display_digits='Product Price'` correctamente. **Opción elegida: A (sin widget monetary).**

```xml
<!-- views/sale_report_views.xml -->
<record id="klo_sale_report_view_tree_price_unit" model="ir.ui.view">
    <field name="name">klo.sale.report.view.list.price_unit</field>
    <field name="model">sale.report</field>
    <field name="inherit_id" ref="sale.sale_report_view_tree"/>
    <field name="arch" type="xml">
        <field name="price_unit" position="replace">
            <field name="price_unit" avg="Average"/>
        </field>
    </field>
</record>
```

> **Decisión confirmada (2026-04-17):** Se usa **Opción A** — sin widget monetary. El campo muestra los decimales respetando la precisión `Product Price` configurada en el sistema. No se muestra el símbolo de moneda (€).

### 3. Herencia de la vista pivot `view_order_product_pivot`

Añadir `price_unit` como medida disponible en el pivot:

```xml
<record id="klo_view_order_product_pivot_price_unit" model="ir.ui.view">
    <field name="name">klo.sale.report.pivot.price_unit</field>
    <field name="model">sale.report</field>
    <field name="inherit_id" ref="sale.view_order_product_pivot"/>
    <field name="arch" type="xml">
        <field name="product_uom_qty" position="after">
            <field name="price_unit" type="measure"/>
        </field>
    </field>
</record>
```

---

## Estructura del módulo a crear

```
klo_sale_report_price_unit_decimals/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_report.py
├── views/
│   └── sale_report_views.xml
└── static/
    └── description/
        ├── icon.png          (logo KLO)
        └── Technical_document.md
```

### `__manifest__.py`

```python
{
    'name': 'KLO - Sale Report Price Unit Decimals',
    'version': '18.0.1.0.0',
    'summary': 'Muestra el Precio Unitario con decimales de "Product Price" en Análisis de Ventas',
    'description': """
        Adaptación del Análisis de Ventas (sale.report) para mostrar el campo
        Precio Unitario (price_unit) respetando la precisión decimal configurada
        en "Product Price" (Ajustes > Técnico > Precisión decimal), tanto en la
        vista lista (sale_report_view_tree) como en la vista pivot
        (view_order_product_pivot).
    """,
    'author': 'KLO',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

---

## Dependencias

- Módulo Odoo base: `sale`
- No requiere módulos OCA ni de terceros.

---

## Consideraciones importantes

### `min_display_digits` vs `digits`
- `min_display_digits='Product Price'`: muestra **como mínimo** los decimales configurados en `Product Price`. Si el valor tiene más decimales significativos, puede mostrar más.
- `digits='Product Price'` (con `get_precision`): fuerza exactamente los decimales configurados, truncando o redondeando el resto.
- Para `price_unit` en análisis de ventas se recomienda `min_display_digits` para no perder precisión en precios con muchos decimales.

### Widget `monetary` vs Float puro
- `widget="monetary"`: muestra símbolo de moneda, pero los decimales los controla `res.currency` (campo `decimal_places`), **no** la precisión `Product Price`.
- **Sin widget** (Float): respeta `min_display_digits='Product Price'` correctamente.
- **✅ Decisión confirmada (2026-04-17): Opción A — sin widget monetary.** Se muestran los decimales según `Product Price` sin símbolo de moneda.

### Vista pivot
- En la vista pivot, los campos de tipo `measure` (medida) muestran el valor agregado (`avg` para `price_unit`).
- El formato de decimales en pivot está controlado por el campo del modelo, por lo que con `min_display_digits='Product Price'` en el modelo debería aplicarse también aquí.

---

## Referencias de archivos base (Odoo 18)

| Archivo | Ruta |
|---|---|
| Modelo `sale.report` | `/opt/odoo18_desarrollo/odoo/addons/sale/report/sale_report.py` |
| Vistas `sale.report` | `/opt/odoo18_desarrollo/odoo/addons/sale/report/sale_report_views.xml` |
| Modelo `sale.order.line` | `/opt/odoo18_desarrollo/odoo/addons/sale/models/sale_order_line.py` |
| Modelo `product.template` | `/opt/odoo18_desarrollo/odoo/addons/product/models/product_template.py` |

---

## IDs XML de vistas a heredar

| Vista | XML ID completo |
|---|---|
| Lista Análisis de Ventas | `sale.sale_report_view_tree` |
| Pivot Análisis de Ventas | `sale.view_order_product_pivot` |
| Gráfico Análisis de Ventas | `sale.view_order_product_graph` |
| Búsqueda Análisis de Ventas | `sale.view_order_product_search` |

---

## Instrucciones para la IA al ejecutar el desarrollo

1. Crear el módulo en `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_sale_report_price_unit_decimals/`
2. Copiar el logotipo KLO en `static/description/icon.png`
3. Heredar el modelo `sale.report` para añadir `min_display_digits='Product Price'` al campo `price_unit`
4. Heredar la vista `sale.sale_report_view_tree` para ajustar el widget del campo `price_unit`
5. Heredar la vista `sale.view_order_product_pivot` para añadir `price_unit` como medida
6. Actualizar el módulo con: `-u klo_sale_report_price_unit_decimals`
7. Verificar en `Ventas → Informes → Ventas` que los decimales del Precio Unitario son correctos en lista y pivot
8. Generar `Technical_document.md` con la documentación técnica final



