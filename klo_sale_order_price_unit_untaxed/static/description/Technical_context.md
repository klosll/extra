# KLO — Sale Order Price Unit Untaxed

**Nombre técnico:** `klo_sale_order_price_unit_untaxed`  
**Versión:** 18.0.1.0.0  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** LGPL-3  
**Categoría:** Sales / Sales  
**Dependencias:** `sale`, `portal`  
**Ubicación:** `extra-addons/klo/extra/klo_sale_order_price_unit_untaxed`

---

## Descripción

Módulo de adaptación que sustituye el precio unitario mostrado en el informe PDF
y en la vista previa del portal de los presupuestos y pedidos de venta, mostrando
el precio **sin impuestos** en lugar del precio con IVA incluido.

Afecta a los siguientes puntos de la aplicación:

- Informe PDF de presupuesto/pedido (`sale.report_saleorder_document`)
- Vista previa del portal — botón *Vista previa* (`action_preview_sale_order`) — template `sale.sale_order_portal_content`

---

## Estructura del módulo

```
klo_sale_order_price_unit_untaxed/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line.py
├── report/
│   └── sale_report_templates.xml
└── static/
    └── description/
        ├── icon.png
        └── Tecnical_document.md
```

---

## Modelo: `sale.order.line`

**Archivo:** `models/sale_order_line.py`

Se hereda el modelo `sale.order.line` y se añade el campo computado `price_unit_untaxed`.

### Campo añadido

| Atributo      | Valor                          |
|---------------|-------------------------------|
| Nombre        | `price_unit_untaxed`          |
| Tipo          | `Float`                       |
| String        | `Precio unitario (sin IVA)`   |
| Digits        | `Product Price`               |
| Computed      | Sí                            |
| Store         | `False`                       |

### Dependencias del compute

```
price_unit, tax_id, product_id, currency_id, order_id.partner_id
```

### Lógica de cálculo

```python
@api.depends('price_unit', 'tax_id', 'product_id', 'currency_id', 'order_id.partner_id')
def _compute_price_unit_untaxed(self):
    for line in self:
        if line.tax_id:
            taxes_result = line.tax_id.compute_all(
                line.price_unit,
                currency=line.currency_id,
                quantity=1.0,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.price_unit_untaxed = taxes_result['total_excluded']
        else:
            line.price_unit_untaxed = line.price_unit
```

El método `compute_all` de `account.tax` devuelve un diccionario con la clave
`total_excluded`, que representa el precio base sin impuestos.  
Si la línea no tiene impuestos asignados, se devuelve directamente `price_unit`.

---

## Templates QWeb modificados

**Archivo:** `report/sale_report_templates.xml`

### 1. `sale.report_saleorder_document` — Informe PDF

**ID del template heredado:** `report_saleorder_document_untaxed_price`

Se reemplaza la celda `td[@name='td_priceunit']` en el cuerpo de la tabla de líneas
para mostrar `line.price_unit_untaxed` formateado como moneda:

```xml
<xpath expr="//td[@name='td_priceunit']" position="replace">
    <td name="td_priceunit" class="text-end text-nowrap">
        <span
            t-out="line.price_unit_untaxed"
            t-options='{"widget": "monetary", "display_currency": doc.currency_id}'
        />
    </td>
</xpath>
```

---

### 2. `sale.sale_order_portal_content` — Vista previa del portal

**ID del template heredado:** `sale_order_portal_content_untaxed_price`

Se aplican dos XPaths:

**XPath 1** — Precio unitario (con soporte de tachado por descuento):

```xml
<xpath expr="//div[@t-field='line.price_unit']" position="replace">
    <div
        t-if="line.discount >= 0"
        t-field="line.price_unit_untaxed"
        t-att-style="line.discount and 'text-decoration: line-through' or None"
        t-att-class="(line.discount and 'text-danger' or '') + ' text-end'"
    />
</xpath>
```

**XPath 2** — Precio con descuento aplicado:

```xml
<xpath expr="//div[@t-if='line.discount']" position="replace">
    <div t-if="line.discount">
        <t t-out="(1 - line.discount / 100.0) * line.price_unit_untaxed"
           t-options='{"widget": "float", "decimal_precision": "Product Price"}'/>
    </div>
</xpath>
```

---

## Comportamiento por tipo de impuesto

| Situación | Resultado en columna Precio Unitario |
|---|---|
| Impuesto configurado como **precio incluido** | Se extrae el precio base sin IVA (`compute_all → total_excluded`) |
| Impuesto configurado como **precio excluido** | El precio ya es sin IVA; `total_excluded` coincide con `price_unit` |
| Sin impuestos en la línea | Se muestra directamente `price_unit` |
| Línea con descuento | El precio tachado y el precio con descuento aplican sobre `price_unit_untaxed` |

---

## Instalación y actualización

Para instalar el módulo desde la interfaz de Odoo:

1. Activar el modo desarrollador.
2. Ir a **Ajustes → Aplicaciones → Actualizar lista de aplicaciones**.
3. Buscar `klo_sale_order_price_unit_untaxed` e instalar.

Para actualizar desde línea de comandos:

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_sale_order_price_unit_untaxed \
    --stop-after-init
```

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)

