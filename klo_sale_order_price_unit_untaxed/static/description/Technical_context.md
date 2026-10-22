# KLO — Sale Order Price Unit Untaxed

**Nombre técnico:** `klo_sale_order_price_unit_untaxed`  
**Versión:** 18.0.2.0.1  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** AGPL-3  
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
        └── Technical_context.md
```

---

## Modelo: `sale.order.line`

**Archivo:** `models/sale_order_line.py`

Se hereda el modelo `sale.order.line` y se añade el campo computado `price_unit_untaxed`.

### Campo añadido

| Atributo          | Valor                         |
|------------------|-------------------------------|
| Nombre           | `price_unit_untaxed`          |
| Tipo             | `Float`                       |
| String           | `Precio unitario (sin IVA)`   |
| min_display_digits | `Product Price`             |
| Computed         | Sí                            |
| Store            | `False`                       |

### Dependencias del compute

```
price_unit, tax_id, product_id, currency_id, order_id.partner_id, display_type
```

`display_type` se incluye en el `@api.depends` porque el compute ramifica según ese
campo (líneas de producto frente a secciones/notas).

### Lógica de cálculo

```python
ESCALA = 10000.0


@api.depends('price_unit', 'tax_id', 'product_id', 'currency_id', 'order_id.partner_id', 'display_type')
def _compute_price_unit_untaxed(self):
    for line in self:
        # Simetría con el módulo de factura: secciones y notas reciben 0.0
        # sin pasar por compute_all. En sale.order.line las líneas de
        # producto tienen display_type vacío (False), no 'product'.
        if line.display_type:
            line.price_unit_untaxed = 0.0
            continue
        if line.tax_id:
            taxes_result = line.tax_id.compute_all(
                line.price_unit,
                currency=line.currency_id,
                quantity=ESCALA,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.price_unit_untaxed = taxes_result['total_excluded'] / ESCALA
        else:
            line.price_unit_untaxed = line.price_unit
```

El método `compute_all` de `account.tax` devuelve un diccionario con la clave
`total_excluded`, que representa el precio base sin impuestos.  
Si la línea no tiene impuestos asignados, se devuelve directamente `price_unit`.
Las líneas de sección y nota (`display_type` informado) reciben `0.0` sin pasar
por `compute_all`.

**Escalado de la cantidad (`ESCALA = 10000.0`):** `compute_all` redondea SIEMPRE
los totales a la precisión de la moneda (céntimos): con `quantity=1.0` devolvería
la base unitaria ya redondeada a 2 decimales (p. ej. `1.41` en lugar de `1.416669`).
Al llamar con `quantity=ESCALA` y dividir el total entre `ESCALA`, el error de
redondeo se divide entre `ESCALA` (depende de la precisión de la moneda: con
céntimos, del orden de 5e-7; con monedas sin decimales puede ser mayor, del orden
de 5e-5), suficiente para presentar 6 decimales. La técnica es lineal para
impuestos porcentuales y de importe fijo, que se multiplican por la cantidad, por
lo que el precio unitario resultante no varía.

No se usa un API 'sin redondeo' del motor de impuestos porque Odoo 18 no expone
públicamente la base unitaria sin redondear (`compute_all` devuelve
`total_excluded` ya redondeado a la moneda; `raw_total_excluded` es interno):
escalar la cantidad evita tocar internals privados.

---

## Templates QWeb modificados

**Archivo:** `report/sale_report_templates.xml`

### 1. `sale.report_saleorder_document` — Informe PDF

**ID del template heredado:** `report_saleorder_document_untaxed_price`

Se reemplaza la celda `td[@name='td_priceunit']` en el cuerpo de la tabla de líneas
para mostrar `line.price_unit_untaxed`. El span usa `t-field`, que toma el formato
del campo (`min_display_digits='Product Price'`): muestra los mismos decimales que
`price_unit` en el formulario y sin símbolo de moneda:

```xml
<xpath expr="//td[@name='td_priceunit']" position="replace">
    <td name="td_priceunit" class="text-end text-nowrap">
        <span t-field="line.price_unit_untaxed"/>
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

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-04-13 | Versión inicial |
| 18.0.2.0.0 | 2026-10-22 | Precisión y formato: el campo pasa de `digits='Product Price'` a `min_display_digits='Product Price'`; el compute llama a `compute_all` con `quantity=ESCALA` (10000.0) y divide `total_excluded` entre `ESCALA` para anular el redondeo a céntimos; el span del informe pasa de `t-out` + widget `monetary` a `t-field` (mismos decimales que el formulario, sin símbolo de moneda) |
| 18.0.2.0.1 | 2026-10-22 | Licencia unificada a AGPL-3 (antes licencia de tipo Lesser), conforme a AGENTS.md |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)

