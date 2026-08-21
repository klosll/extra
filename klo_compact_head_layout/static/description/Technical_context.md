# KLO — Compact Head Layout

**Nombre técnico:** `klo_compact_head_layout`  
**Versión:** 18.0.0.1  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** AGPL-3  
**Categoría:** Uncategorized  
**Dependencias:** `account`, `web`, `klo_report_layout_small_font_header`  
**Ubicación:** `extra-addons/klo/extra/klo_compact_head_layout`

---

## Descripción

Módulo de adaptación que sustituye la cabecera estándar de los informes QWeb de Odoo
por una cabecera compacta en una única fila, mostrando en paralelo:

- **Izquierda (50%):** Logo de la empresa + datos de contacto / detalles de empresa
- **Centro (col-3, condicional):** Dirección de entrega — solo si existe y es diferente a la del cliente
- **Derecha (col-3 / col-6 dinámico):** Datos del cliente / destinatario

El ancho del bloque del cliente se adapta dinámicamente:
- `col-3` cuando hay dirección de entrega (comparte el 50% derecho con ella)
- `col-6` cuando **no** hay dirección de entrega (ocupa todo el espacio derecho disponible)

Afecta a todos los informes que usan `web.external_layout`, así como específicamente a:

- Facturas (`account.report_invoice_document`)
- Presupuestos y pedidos de venta (`sale.report_saleorder_document`)
- Albaranes de entrega (`stock.report_delivery_document`)

---

## Estructura del módulo

```
klo_compact_head_layout/
├── __init__.py
├── __manifest__.py
├── reports/
│   └── report_sale_picking_invoice_documents.xml
├── views/
│   ├── report_assets.xml
│   └── report_templates.xml
└── static/
    └── description/
        ├── icon.png
        └── Tecnical_document.md
```

---

## Parámetro de sistema utilizado

El módulo depende del parámetro de sistema provisto por `klo_report_layout_small_font_header`:

| Parámetro                              | Valor por defecto | Descripción                                      |
|----------------------------------------|-------------------|--------------------------------------------------|
| `klo.report_layout_small_font_header`  | `12`              | Tamaño de fuente (px) de la cabecera del informe |

Se obtiene mediante:
```python
request.env['ir.config_parameter'].sudo().get_param('klo.report_layout_small_font_header', '12')
```

---

## Template principal: `klo_external_layout_compact`

**Archivo:** `views/report_templates.xml`  
**Hereda de:** `web.external_layout_standard`  
**Posición XPath:** `replace` sobre `//div[@t-attf-class='header o_company_#{company.id}_layout']`

### Estructura de la cabecera

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo empresa]   [w-50]  │  [Entrega col-3]*  │ [Cliente col-3/col-6] │
│  [Datos empresa]          │  (condicional)      │ (dinámico)            │
└─────────────────────────────────────────────────────────────────┘
* Solo se renderiza si show_shipping == True
```

### Variable `show_shipping`

Variable QWeb calculada en tiempo de renderizado para determinar si se debe mostrar
el bloque de dirección de entrega y ajustar el ancho del bloque de cliente:

```xml
<t t-set="show_shipping"
   t-value="(o_model in ['sale.order', 'account.move']
             and bool(o.partner_shipping_id)
             and o.partner_shipping_id != o.partner_id)
            or o_model == 'stock.picking'"/>
```

| Condición                                                                 | `show_shipping` |
|---------------------------------------------------------------------------|-----------------|
| `sale.order` / `account.move` con `partner_shipping_id` ≠ `partner_id`  | `True`          |
| `stock.picking` (albarán)                                                 | `True`          |
| Cualquier otro caso (factura sin entrega diferente, presupuesto, etc.)    | `False`         |

### Bloque dirección de entrega — Pedidos y Facturas

Solo se renderiza si el modelo es `sale.order` o `account.move` y la dirección de
entrega existe y es distinta a la del cliente:

```xml
<t t-if="o_model in ['sale.order', 'account.move']
         and o.partner_shipping_id
         and (o.partner_shipping_id != o.partner_id)">
    <div class="col-3" ...>
        <!-- Nombre, CIF/NIF, calle, CP, ciudad, país del partner_shipping_id -->
    </div>
</t>
```

Campos renderizados: `partner_shipping_id.name`, `partner_shipping_id.comercial` (si existe),
`partner_shipping_id.vat`, `partner_shipping_id.street`, `partner_shipping_id.zip`,
`partner_shipping_id.city`, `partner_shipping_id.country_id.name`.

### Bloque dirección de entrega — Albaranes

Solo se renderiza si el modelo es `stock.picking`. En este caso la dirección de entrega
siempre coincide con `partner_id`:

```xml
<t t-if="o_model == 'stock.picking'">
    <div class="col-3" ...>
        <!-- Nombre, CIF/NIF, calle, CP, ciudad, país del partner_id -->
    </div>
</t>
```

### Bloque dirección del cliente (ancho dinámico)

```xml
<div t-attf-class="#{'col-3' if show_shipping else 'col-6'}"
     style="margin-bottom: 5px; font-size: {{font_size}}px; ...">
```

| `show_shipping` | Clase aplicada | Ancho efectivo |
|-----------------|---------------|----------------|
| `True`          | `col-3`       | 25% del ancho total |
| `False`         | `col-6`       | 50% del ancho total (se amplía hacia la derecha) |

Casos de renderizado del bloque cliente:

- **`account.payment.order`:** Muestra los partners de `payment_line_ids`. Si hay uno solo,
  muestra su nombre, CIF/NIF, dirección. Si hay más de uno, muestra "Varios contactos (N)".
- **Caso general (otros modelos):** Muestra `partner_id` con nombre, comercial (si existe),
  CIF/NIF, calle, CP, ciudad, país.

---

## Template de override global: `klo_external_layout`

**Archivo:** `views/report_assets.xml`  
**Hereda de:** `web.external_layout`

Reemplaza el selector de layout de todos los informes para forzar el uso del layout
compacto independientemente de la configuración de layout de la empresa:

```xml
<!-- 1. Reemplaza la rama t-if para usar siempre el layout compacto -->
<xpath expr="//t[@t-if='company.external_report_layout_id']" position="replace">
    <t t-call="klo_compact_head_layout.klo_external_layout_compact">
        <t t-out="0"/>
    </t>
</xpath>

<!-- 2. Elimina la rama t-else del layout estándar para evitar doble renderizado -->
<xpath expr="//t[@t-else='else'][@t-call='web.external_layout_standard']"
       position="replace"/>
```

---

## Templates de documentos específicos

**Archivo:** `reports/report_sale_picking_invoice_documents.xml`

Elimina los bloques de dirección duplicados que ya incluyen los templates estándar
de Odoo para evitar que la dirección aparezca dos veces (una en la cabecera compacta
y otra en el cuerpo del documento):

### Facturas — `klo_invoice_report_document_compact`

```xml
<template id="klo_invoice_report_document_compact"
          inherit_id="account.report_invoice_document">
    <!-- Elimina el primer div.row que contiene los datos del cliente en la factura estándar -->
    <xpath expr="//div[@class='row'][1]" position="replace"/>
</template>
```

### Pedidos/Presupuestos — `klo_report_saleorder_document_compact`

```xml
<template id="klo_report_saleorder_document_compact"
          inherit_id="sale.report_saleorder_document">
    <!-- Elimina el bloque t-set address del template estándar -->
    <xpath expr="//t[@t-set='address']" position="replace"/>
    <!-- Elimina el bloque t-set information_block del template estándar -->
    <xpath expr="//t[@t-set='information_block']" position="replace"/>
</template>
```

### Albaranes — `klo_report_delivery_document_compact`

```xml
<template id="klo_report_delivery_document_compact"
          inherit_id="stock.report_delivery_document">
    <!-- Elimina el bloque t-set address del template estándar -->
    <xpath expr="//t[@t-set='address']" position="replace"/>
</template>
```

---

## Comportamiento por tipo de documento

| Modelo              | Entrega mostrada                          | Ancho bloque cliente |
|---------------------|-------------------------------------------|----------------------|
| `sale.order`        | Solo si `partner_shipping_id` ≠ `partner_id` | `col-6` sin entrega / `col-3` con entrega |
| `account.move`      | Solo si `partner_shipping_id` ≠ `partner_id` | `col-6` sin entrega / `col-3` con entrega |
| `stock.picking`     | Siempre (`partner_id`)                    | `col-3` (siempre hay entrega) |
| `account.payment.order` | No aplica                             | `col-6` (sin entrega) |
| Otros modelos       | No aplica                                 | `col-6` (sin entrega) |

---

## Notas para futuras adaptaciones

- **Añadir soporte a un nuevo modelo:** Ampliar la condición `show_shipping` y los bloques
  `t-if` de dirección de entrega con el nuevo `o._name`.
- **Cambiar el ancho de las columnas:** Modificar los valores `col-3` / `col-6` en el
  `t-attf-class` del bloque cliente y en los divs de entrega.
- **Añadir nuevos campos en la dirección del cliente:** Editar el bloque "Caso general"
  dentro del div del cliente en `report_templates.xml`.
- **Eliminar bloques duplicados de un nuevo documento:** Añadir un nuevo template en
  `reports/report_sale_picking_invoice_documents.xml` heredando del template del documento.
- **Ajustar el tamaño de fuente:** Modificar el parámetro de sistema
  `klo.report_layout_small_font_header` desde **Ajustes → Parámetros técnicos → Parámetros del sistema**.

---

## Instalación y actualización

Para instalar el módulo desde la interfaz de Odoo:

1. Activar el modo desarrollador.
2. Ir a **Ajustes → Aplicaciones → Actualizar lista de aplicaciones**.
3. Buscar `klo_compact_head_layout` e instalar.

Para actualizar desde línea de comandos:

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_compact_head_layout \
    --stop-after-init
```

---

## Historial de cambios

| Versión   | Fecha      | Descripción                                                                 |
|-----------|------------|-----------------------------------------------------------------------------|
| 18.0.0.1  | 2026-04-14 | Adaptación de ancho dinámico del bloque cliente según presencia de dirección de entrega (`show_shipping`). Refactorización de condiciones en `report_templates.xml`. |
| 18.0.0.1  | (inicial)  | Creación del layout compacto. Soporte para `sale.order`, `account.move`, `stock.picking`, `account.payment.order`. |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)

