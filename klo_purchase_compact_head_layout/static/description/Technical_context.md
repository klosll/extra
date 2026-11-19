# KLO — Cabecera compacta para compra

**Nombre técnico:** `klo_purchase_compact_head_layout`  
**Versión:** 18.0.0.1.0  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** AGPL-3  
**Categoría:** Purchase  
**Dependencias:** `purchase`, `klo_compact_head_layout`  
**Ubicación:** `extra-addons/klo/extra/klo_purchase_compact_head_layout`

---

## Descripción funcional

Módulo de adaptación que extiende la cabecera compacta global definida por
`klo_compact_head_layout` (template `klo_compact_head_layout.klo_external_layout_compact`)
para dar soporte a los documentos de compra:

- **Pedido de compra** (`purchase.order`) y **Solicitud de presupuesto** (`purchase.order`,
  que comparte template de documento con los pedidos)
- Muestra **"Proveedor:"** en lugar de **"Cliente:"** cuando el documento es un
  `purchase.order` (el `partner_id` de una compra es el proveedor).
- Muestra la **dirección de entrega** (`o.dest_address_id`) en la cabecera compacta,
  en paralelo con el bloque del proveedor.
- Evita que la dirección del proveedor y la dirección de entrega aparezcan **duplicadas**:
  anula a `None` las variables `address` e `information_block` de los templates de compra
  de Odoo (insertando un `t-set` justo antes de `<div class="page">`), de modo que el
  `address_layout` no imprima la dirección duplicada en el cuerpo del documento.

El resultado es una cabecera compacta de una única fila en la que, para `purchase.order`:

- **Izquierda (50%):** Logo de la empresa + datos de la empresa.
- **Centro (col-3, condicional):** Dirección de entrega (`dest_address_id`) — solo si existe.
- **Derecha (col-3 / col-6 dinámico):** Datos del **proveedor**.

El ancho del bloque del proveedor se adapta dinámicamente gracias a la variable
`show_shipping` de la cabecera compacta, ampliada por este módulo para incluir
`purchase.order`.

---

## Cambios sobre `klo_external_layout_compact`

**Archivo:** `views/purchase_compact_layout.xml`  
**Template:** `klo_external_layout_compact_purchase`  
**Hereda de:** `klo_compact_head_layout.klo_external_layout_compact`

Se realizan 3 cambios mediante XPath:

### 1. Ampliar la variable `show_shipping`

Se sustituye el valor del atributo `t-value` del `t-set` `show_shipping` para incluir
`purchase.order` cuando tiene dirección de entrega definida:

```xml
<xpath expr="//t[@t-set='show_shipping']" position="attributes">
    <attribute name="t-value">(o_model in ['sale.order', 'account.move'] and bool(o.partner_shipping_id) and o.partner_shipping_id != o.partner_id) or o_model == 'stock.picking' or (o_model == 'purchase.order' and bool(o.dest_address_id))</attribute>
</xpath>
```

| Condición                                                              | `show_shipping` |
|------------------------------------------------------------------------|-----------------|
| `sale.order` / `account.move` con `partner_shipping_id` ≠ `partner_id` | `True`          |
| `stock.picking` (albarán)                                              | `True`          |
| `purchase.order` con `dest_address_id` definido (nuevo)                | `True`          |
| Cualquier otro caso                                                     | `False`         |

Al activar `show_shipping` para compra, el bloque del proveedor pasa a `col-3`
(comparte el 50% derecho con la dirección de entrega) en lugar de `col-6`.

### 2. Bloque de dirección de entrega para compra

Se inserta, justo después del bloque de entrega de albaranes
(`t[@t-if="o_model == 'stock.picking'"]`), un bloque condicional que renderiza
`o.dest_address_id` para `purchase.order`:

```xml
<xpath expr="//t[@t-if=&quot;o_model == 'stock.picking'&quot;]" position="after">
    <t t-if="o_model == 'purchase.order' and o.dest_address_id">
        <div class="col-3" ...>
            <!-- Nombre, comercial, CIF/NIF, calle, CP, ciudad, país, tfno., email de o.dest_address_id -->
        </div>
    </t>
</xpath>
```

Campos renderizados: `dest_address_id.name`, `dest_address_id.comercial` (si existe),
`dest_address_id.vat`, `dest_address_id.street`, `dest_address_id.zip`,
`dest_address_id.city`, `dest_address_id.country_id.name`, `dest_address_id.phone`,
`dest_address_id.email`.

### 3. Etiqueta "Proveedor:" en lugar de "Cliente:"

Se reemplaza el `<strong>Cliente:</strong>` del bloque general del cliente
(`t[@t-else]`) por una etiqueta dinámica:

```xml
<xpath expr="//t[@t-else]//strong[normalize-space()='Cliente:']" position="replace">
    <strong><t t-esc="'Proveedor:' if o_model == 'purchase.order' else 'Cliente:'"/></strong>
</xpath>
```

Así, para `purchase.order` el bloque del cliente muestra **"Proveedor:"**, y para el
resto de modelos mantiene **"Cliente:"**.

---

## Eliminación de bloques duplicados en compra

**Archivo:** `reports/purchase_order_report.xml`

Igual que `klo_compact_head_layout` evita los bloques de dirección duplicados de
venta/factura/albarán, este módulo evita que la dirección del proveedor y la de entrega
aparezcan dos veces (una en la cabecera compacta y otra en el cuerpo del documento).

En lugar de eliminar los bloques con `position="replace"`, se **anulan a `None`** las
variables `address` e `information_block` insertando un `t-set` justo antes de
`<div class="page">`. Así el `address_layout` no imprime la dirección duplicada y,
además, **no se rompe el `t-if`/`t-else` que añade `purchase_stock`** justo después del
`t-if="o.dest_address_id"` (eliminar ese `t-if` dejaría huérfano el `<t t-else="">` y
provocaría `SyntaxError: t-elif directive must be preceded by t-if or t-elif directive`).

### Pedido de compra — `klo_purchase_order_document_compact`

```xml
<template id="klo_purchase_order_document_compact"
          inherit_id="purchase.report_purchaseorder_document">
    <xpath expr="//div[@class='page']" position="before">
        <t t-set="address" t-value="None"/>
        <t t-set="information_block" t-value="None"/>
    </xpath>
</template>
```

### Solicitud de presupuesto — `klo_purchase_quotation_document_compact`

```xml
<template id="klo_purchase_quotation_document_compact"
          inherit_id="purchase.report_purchasequotation_document">
    <xpath expr="//div[@class='page']" position="before">
        <t t-set="address" t-value="None"/>
        <t t-set="information_block" t-value="None"/>
    </xpath>
</template>
```

> **Nota:** en el template de pedido de compra, `information_block` es la variable que
> rellena el bloque `t-if="o.dest_address_id"` (encabezado "Shipping address" + dirección
> de entrega). Al anularla a `None`, el `address_layout` no renderiza esa dirección, sin
> tocar la estructura `t-if`/`t-else` del template original.

---

## Estructura del módulo

```
klo_purchase_compact_head_layout/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py
├── reports/
│   └── purchase_order_report.xml
├── views/
│   └── purchase_compact_layout.xml
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

El módulo no define modelos Python propios: únicamente reutiliza el layout compacto
existente mediante herencia de templates QWeb (`models/` está vacío y solo existe por
convención de estructura).

---

## Comportamiento por tipo de documento

| Modelo              | Entrega mostrada                              | Etiqueta bloque derecho |
|---------------------|-----------------------------------------------|-------------------------|
| `purchase.order`    | `dest_address_id` (si existe)                 | "Proveedor:"            |
| `sale.order`        | `partner_shipping_id` (si ≠ `partner_id`)     | "Cliente:"              |
| `account.move`      | `partner_shipping_id` (si ≠ `partner_id`)     | "Cliente:"              |
| `stock.picking`     | `partner_id`                                  | "Cliente:"              |
| `account.payment.order` | No aplica                                 | "Cliente(s):"           |
| Otros modelos       | No aplica                                     | "Cliente:"              |

---

## Parámetro de sistema utilizado

Heredado de `klo_compact_head_layout` / `klo_report_layout_small_font_header`:

| Parámetro                              | Valor por defecto | Descripción                                      |
|----------------------------------------|-------------------|--------------------------------------------------|
| `klo.report_layout_small_font_header`  | `12`              | Tamaño de fuente (px) de la cabecera del informe |

---

## Instalación y actualización

Para instalar el módulo desde la interfaz de Odoo:

1. Activar el modo desarrollador.
2. Ir a **Ajustes → Aplicaciones → Actualizar lista de aplicaciones**.
3. Buscar `klo_purchase_compact_head_layout` e instalar.

Para actualizar desde línea de comandos:

```bash
python3 /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_purchase_compact_head_layout \
    --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción                                                                 |
|------------|------------|-----------------------------------------------------------------------------|
| 18.0.0.1.0 | 2026-11-19 | Creación del módulo. Soporte de `purchase.order` en la cabecera compacta: proveedor + dirección de entrega `dest_address_id`, sin duplicar dirección. |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)
