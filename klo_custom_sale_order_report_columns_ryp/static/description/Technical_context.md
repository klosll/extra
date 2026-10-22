<!-- Copyright 2026 KLO Ingeniería Informática S.L.L.
     License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). -->
# klo_custom_sale_order_report_columns_ryp

> Documento técnico para módulos `klo_*`, orientado a ser procesado por una IA para futuros
> ajustes y desarrollos. Cliente: RYP.

## Módulo

| Campo            | Valor |
|------------------|-------|
| Nombre técnico   | `klo_custom_sale_order_report_columns_ryp` |
| Nombre legible   | KLO - Custom Sale Order Report Columns RYP |
| Versión          | `18.0.2.2.0` |
| Autor            | KLO Ingenieria Informatica S.L.L. |
| Licencia         | AGPL-3 |
| Categoría        | Sales/Sales |
| Dependencias     | `sale`, `klo_sale_order_price_unit_untaxed`, `klo_report_saleorder_no_taxes_column`, `klo_invoice_report_price_unit_untaxed` |
| Ubicación        | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_custom_sale_order_report_columns_ryp` |
| Fecha creación   | 2026-10-20 |
| Odoo versión     | 18.0 Community |
| Base de datos    | `ryp_dev` (leída de `db_name` en `/opt/odoo18_desarrollo/config/odoo.conf`) |

## Descripción

Personalización de las columnas de la tabla de líneas de los informes PDF de pedido de
venta (`sale.report_saleorder_document`) y factura (`account.report_invoice_document`)
para el cliente RYP:

* Cambia la cabecera de la columna de precio unitario a **Precio U** en ambos documentos.
* Añade una nueva columna **Neto** antes de "Importe": precio unitario sin impuestos con el
  descuento aplicado (`price_unit_untaxed` rebajado según `discount`).
* Sustituye el valor de la columna **Importe**: en lugar de `line.price_total` /
  `line.price_subtotal` (elegidos por el core según la política de precios), el Importe
  muestra el subtotal del documento (`price_subtotal`), que cuadra exactamente con
  base/IVA/total.

Desde 18.0.2.0.0 el módulo añade lógica Python mínima: el campo computado
`price_unit_net` en `sale.order.line` y `account.move.line` (Neto =
`price_unit_untaxed` con el descuento aplicado, sin redondeo), renderizado con
`t-field` para mostrar los mismos decimales que el campo «Precio unitario» del
formulario (precisión decimal «Product Price»). El resto se resuelve en QWeb
reutilizando `price_unit_untaxed` de las dependencias
(`klo_sale_order_price_unit_untaxed` en `sale.order.line`,
`klo_invoice_report_price_unit_untaxed` en `account.move.line`), y convive con el
ocultado de «Impuestos» del pedido (`klo_report_saleorder_no_taxes_column`) y con la
agrupación por albarán de la factura (`account_invoice_report_grouped_by_picking`).

## Campo(s) añadido(s)

* **`sale.order.line.price_unit_net`** (Float, string `Neto`, compute
  `_compute_price_unit_net` con `@api.depends('price_unit_untaxed', 'discount')`,
  `store=False`): Neto = precio unitario sin impuestos con el descuento aplicado. Se
  define con `min_display_digits='Product Price'` (sin `digits`) para **mimetizar el
  `price_unit` del core de Odoo 18**: el render con `t-field` le aplica los mismos
  decimales que el campo «Precio unitario» del formulario. El valor se mantiene
  **sin redondear** (el redondeo es solo de presentación).
* **`account.move.line.price_unit_net`** (definición idéntica: Float, string `Neto`,
  compute `_compute_price_unit_net` con `@api.depends('price_unit_untaxed', 'discount')`,
  `store=False`, `min_display_digits='Product Price'` sin `digits`): Neto de la línea de
  factura; base de la columna "Neto" en `account.report_invoice_document`.
* Reutiliza `sale.order.line.price_unit_untaxed` (Float, compute `_compute_price_unit_untaxed`,
  añadido por `klo_sale_order_price_unit_untaxed`): precio unitario sin impuestos de la línea
  de pedido; base de `price_unit_net` en el pedido.
* Reutiliza `account.move.line.price_unit_untaxed` (añadido por
  `klo_invoice_report_price_unit_untaxed`): precio unitario sin impuestos de la línea de
  factura; base de `price_unit_net` en la factura.
* Convive con el ocultado de la columna "Impuestos" (`th_taxes`/`td_taxes`) del pedido
  realizado por `klo_report_saleorder_no_taxes_column` sobre el mismo informe.
* Añade las columnas QWeb **"Neto"** (`th_net`/`td_net`) en pedido y factura, sustituye el
  valor de **"Importe"** dentro de `td_subtotal` y cambia las cabeceras **"Precio U"**
  (`th_priceunit`) de ambos documentos.

## Dependencias

| Módulo | Tipo | Ruta | Motivo |
|--------|------|------|--------|
| `sale` | Núcleo Odoo | `/opt/odoo18_desarrollo/odoo/addons/sale` | Template base `sale.report_saleorder_document` (nodos `th_priceunit`, `th_subtotal`, `td_subtotal`) |
| `klo_sale_order_price_unit_untaxed` | KLO | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_sale_order_price_unit_untaxed` | Aporta el campo `price_unit_untaxed` en `sale.order.line`, base de la columna "Neto" del pedido |
| `klo_report_saleorder_no_taxes_column` | KLO | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_report_saleorder_no_taxes_column` | Aporta el ocultado de la columna "Impuestos" (`th_taxes`/`td_taxes`) del mismo informe; sus xpaths no interfieren con los de este módulo |
| `klo_invoice_report_price_unit_untaxed` | KLO | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_invoice_report_price_unit_untaxed` | Aporta el campo `price_unit_untaxed` en `account.move.line`, base de la columna "Neto" de la factura; su dependencia del núcleo (`account`) aporta el template base `account.report_invoice_document` |

## Lógica

Fórmulas exactas (campo computado en Python + expresiones en los templates): el campo
propio guarda el valor sin redondear (el redondeo es solo de presentación).

* **Neto** (campo `price_unit_net`, columna `td_net`, en pedido y factura):
  `Neto = price_unit_untaxed × (1 − (discount or 0.0) / 100.0)` **sin redondear**: el
  campo guarda el valor tal cual y el redondeo es solo de presentación (`t-field`).
* **Importe** (sustituye el valor del `td_subtotal`, en pedido y factura):
  Importe = `line.price_subtotal` (subtotal de Odoo), siempre sin impuestos, igual en
  pedido y factura; así el sumatorio cuadra exactamente con la base/IVA/total. En la
  factura, las filas con cantidad parcial por albarán muestran la parte proporcional
  (ver coexistencia más abajo).

  Nota (18.0.2.1.0): hasta esa versión el Importe se calculaba como `Cantidad × Neto`;
  con impuestos precio incluido Odoo redondea el impuesto por línea y la base sale por
  diferencia, por lo que `Cantidad × Neto` podía diferir ±0,01 € (ej. pedido V26006289,
  línea 21119: 13,57 vs 13,58). Se cambió a `line.price_subtotal` para cuadrar
  exactamente con base/IVA/total. Precio U y Neto no cambian.
* **Decimales de «Precio U» y «Neto»:** gobernados por la precisión decimal
  «Product Price» de la base de datos (hoy 6 en `ryp_dev`); ambos se renderizan con
  `t-field`, que hereda del campo su formato (`min_display_digits='Product Price'`),
  por lo que se adaptan solos si la precisión cambia.
* **«Importe»** en formato moneda (widget `monetary`, 2 decimales).
* **Precio U**: solo cambia la cabecera de la columna de precio unitario en ambos
  documentos; el valor de la celda es `price_unit_untaxed` (precio unitario sin
  impuestos, **sin descuento**), renderizado con `t-field` por las dependencias; solo
  **Neto** lleva el descuento aplicado.

Detalles de renderizado:

* Pedido: `td_net` replica el `t-if="not line.is_downpayment"` del `td_subtotal` del
  core; el span alternativo del core (`line.price_subtotal`) se elimina sustituyéndolo
  por un nodo vacío `<t/>`; el span de "Importe" usa `t-out="line.price_subtotal"` con
  `t-options='{"widget": "monetary", "display_currency": doc.currency_id}'`.
* Factura: el span original del subtotal (`line.price_subtotal`) NO se elimina, se
  oculta con `style="display:none"` (ver coexistencia); el span de "Importe" usa
  `t-out="line.price_subtotal"` con
  `t-options='{"widget": "monetary", "display_currency": o.currency_id}'` y el `t-if` de
  coexistencia con la agrupación por albarán.
* «Neto»: `<span t-field="line.price_unit_net"/>` en pedido y factura; hereda del
  campo su formato (`min_display_digits='Product Price'`), sin símbolo de moneda.

**Coexistencia con `account_invoice_report_grouped_by_picking`** (agrupación de líneas de
factura por albarán):

* Ese módulo ancla sus herencias en el span del core
  `td_subtotal/span[@t-field='line.price_subtotal']` y fija un `t-if` en él; por eso ese
  span **no se elimina** (sus xpaths dejarían de matchear) y se oculta con `style` en
  lugar de con `t-if`: ese módulo fija el mismo atributo `t-if` en el span y el último en
  aplicarse pisaría al otro.
* El span nuevo de "Importe" lleva
  `t-if="not (lines_group and lines_group['quantity'] != l.quantity)"`, la **negación**
  de la condición del módulo de agrupación: las filas con cantidad parcial por albarán
  muestran SU subtotal proporcional (parte de `l.price_subtotal` según la cantidad
  mostrada); el resto de las filas muestra el nuestro. Así no se duplican importes y
  ambos son sin impuestos.
* `lines_group` y `l` son variables que solo existen con el módulo de agrupación
  instalado; la expresión tolera que no existan porque QWeb resuelve los nombres
  indefinidos como `None`: la condición cae en la rama sin agrupación y se muestra el
  subtotal completo de la línea.

**Separación de columnas numéricas** (desde 18.0.2.2.0):

* Se inyecta un `<style>` justo antes de la tabla `o_main_table` (en pedido y factura)
  con `padding-left: 1mm` para `th.text-end`/`td.text-end`: los datos de las columnas
  numéricas se mezclaban visualmente, agravado por el `padding: 1px` de los módulos de
  fuente pequeña.
* Se aplica a `th` y `td` para mantener cabeceras y valores alineados.
* El scope a `table.o_main_table` evita tocar la tabla de totales (`o_total_table`).
* Cubre también columnas numéricas de terceros (p. ej. «Cantidad secundaria» de
  `sale_order_secondary_unit`), que comparten `text-end`.
* La regla tiene especificidad (0,2,1) frente al `padding: 1px` (0,1,1) de los módulos
  de fuente pequeña, por lo que no hace falta `!important`.

## Vistas modificadas

**Archivo:** `report/sale_order_report_templates.xml`
**Template:** `klo_custom_saleorder_columns_ryp` (hereda `sale.report_saleorder_document`)

| # | XPath | Posición | Cambio |
|---|-------|----------|--------|
| 1 | `//th[@name='th_priceunit']` | `replace` | Sustituye el `th` (en el pedido el texto va directo, sin span) conservando `name`/`class`: cabecera **Precio U** |
| 2 | `//th[@name='th_subtotal']` | `before` | Añade `<th name="th_net">Neto</th>` |
| 3 | `//td[@name='td_subtotal']` | `before` | Añade `td_net` con span `t-field="line.price_unit_net"` y el mismo `t-if` de anticipo que el core |
| 4 | `//td[@name='td_subtotal']/span[@t-field='line.price_total']` | `replace` | Sustituye por span `t-out="line.price_subtotal"` con `t-options` de widget `monetary` (`display_currency`: `doc.currency_id`) → Importe = subtotal de Odoo (siempre sin impuestos, cuadra con base/IVA/total) |
| 5 | `//td[@name='td_subtotal']/span[@t-field='line.price_subtotal']` | `replace` | Sustituye por `<t/>` (no renderiza nada) |
| 6 | //table[hasclass('o_main_table')] | before | Inserta <style> con padding-left 1mm en th/td.text-end de la tabla de líneas (separación de columnas numéricas) |

**Archivo:** `report/account_report_templates.xml`
**Template:** `klo_custom_invoice_columns_ryp` (hereda `account.report_invoice_document`)

| # | XPath | Posición | Cambio |
|---|-------|----------|--------|
| 1 | `//th[@name='th_priceunit']/span` | `replace` | Sustituye el span interno (en la factura la cabecera sí lleva span): cabecera **Precio U** |
| 2 | `//th[@name='th_subtotal']` | `before` | Añade `<th name="th_net">Neto</th>` |
| 3 | `//td[@name='td_subtotal']` | `before` | Añade `td_net` con span `t-field="line.price_unit_net"` |
| 4 | `//td[@name='td_subtotal']/span[@t-field='line.price_subtotal']` | `attributes` | Añade `style="display:none"`; el span NO se elimina (ancla de herencias de terceros) |
| 5 | `//td[@name='td_subtotal']` | `inside` | Añade span con `t-out="line.price_subtotal"` y `t-options` de widget `monetary` (`display_currency`: `o.currency_id`), con el `t-if` de coexistencia con la agrupación por albarán → Importe = subtotal de Odoo |
| 6 | //table[hasclass('o_main_table')] | before | Inserta <style> con padding-left 1mm en th/td.text-end de la tabla de líneas (separación de columnas numéricas) |

**Nota de renderizado:** los spans de «Precio U» (pedido y factura, aportados por
`klo_sale_order_price_unit_untaxed` y `klo_invoice_report_price_unit_untaxed`) y de
«Neto» usan `t-field`, heredando del campo su formato (`min_display_digits='Product
Price'`): mismos decimales que el formulario y sin símbolo de moneda. Los spans de
«Importe» conservan widget monetary (2 decimales).

**Lección de superficie mínima:** en el pedido no se reemplaza el `td` completo (solo se
añaden nodos hermanos o se sustituyen los `span` internos; única excepción: `th_priceunit`,
cuyo texto va directo en el `th`, se reemplaza entero conservando `name` y `class`). En la
factura, el `span` del subtotal no se elimina sino que se oculta con `style`, por las
herencias de terceros que anclan en él.

**Notas:**

* Literales **"Neto"** y **"Precio U"** sin i18n: son texto duro solicitado por el
  cliente; para traducirlos habría que externalizarlos.
* **Riesgo de orden de herencias:** los xpaths anclan en nodos del core que también usan
  módulos de terceros; entre módulos sin dependencia mutua el orden de aplicación no está
  garantizado (ver notas de conflictos y coexistencia).

**Nota de conflictos auditados:**

* `account_invoice_report_grouped_by_picking` (**instalado** en `ryp_dev`): coexistencia
  resuelta como se describe en `## Lógica` (ocultación por `style` y `t-if` negado);
  reauditar el PDF si cambia su implementación.
* `sale_layout_category_hide_detail` (OCA, `oca/sale-reporting`; **no instalado** en
  `ryp_dev`): **riesgo sensible al orden de herencia, NO verificable como compatible a
  priori**. Ese módulo aplica
  `xpath expr="//td[@name='td_subtotal']/span" position="attributes"` añadiendo
  `t-if="... and (not current_section or current_section.show_line_amount)"`, es decir,
  ancla sobre el mismo `span` que este módulo reemplaza. Dos escenarios:
  - Aplicado **después** de este módulo: su xpath matchea el `span` nuevo de "Importe" y
    su `t-if` se añade correctamente (comportamiento esperado).
  - Aplicado **antes**: su `t-if` se añade al `span` original del core
    (`span[@t-field='line.price_total']`), que este módulo sustituye después; el `t-if`
    se pierde y se produce una **regresión funcional silenciosa**: la columna "Importe"
    dejaría de ocultarse al plegar el detalle de sección.
  Como ningún módulo depende del otro (ambos `priority` 16 por defecto), el orden de
  aplicación **no está garantizado**. La inmunización se documenta solo como adaptación
  futura (ver `## Posibles adaptaciones futuras`).
* `sale_order_report_without_price` (OCA, `oca/sale-workflow`, `primary="True"`;
  **no instalado** en `ryp_dev`): oculta `th_subtotal`/`td_subtotal` (y el resto de
  columnas de precio) con `t-if="False"` vía `position="attributes"`, pero no conoce
  `th_net`/`td_net`, nodos añadidos por este módulo. Si se instalara, la columna
  "Neto" quedaría visible en el informe "sin precios". **Riesgo bajo**: no es
  dependencia de este módulo y no se espera coexistencia.
* `l10n_br_sales` y `klo_klo`: **NO coexisten** en `ryp_dev`; ambos modifican los mismos
  informes y se documentan como **riesgo conocido** si en el futuro se llegaran a instalar
  simultáneamente en la misma base de datos.

## Estructura de archivos

```
klo_custom_sale_order_report_columns_ryp/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py                      # Importa sale_order_line y account_move_line
│   ├── sale_order_line.py               # sale.order.line: campo price_unit_net
│   └── account_move_line.py             # account.move.line: campo price_unit_net
├── report/
│   ├── sale_order_report_templates.xml   # Hereda sale.report_saleorder_document (6 xpaths)
│   └── account_report_templates.xml      # Hereda account.report_invoice_document (6 xpaths)
└── static/
    └── description/
        ├── icon.png                      # Icono compartido KLO (copia de _templates)
        └── Technical_context.md          # Este documento
```

## Instalación / Actualización

La base de datos activa se lee de `db_name` en `/opt/odoo18_desarrollo/config/odoo.conf`;
nunca hardcodear otra base (en este proyecto `db_name = ryp_dev`, leída de `config/odoo.conf`).

```bash
# Instalación (primera vez)
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <db_name> -i klo_custom_sale_order_report_columns_ryp --stop-after-init --no-http

# Actualización (tarea de desarrollo habitual)
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <db_name> -u klo_custom_sale_order_report_columns_ryp --stop-after-init --no-http
```

Tras actualizar (imprescindible en el paso a 18.0.2.0.0: se añade el campo Python
`price_unit_net`, por lo que debe ejecutarse `-u` para cargarlo), conviene regenerar un
PDF de pedido y de factura y verificar las columnas «Precio U», «Neto» e «Importe».

## Posibles adaptaciones futuras

* **i18n de "Neto" y "Precio U":** las etiquetas son texto literal pedido por el cliente;
  si se requiriese traducción, externalizar los términos en lugar de dejarlos como texto
  duro.
* **Redondeo:** el Importe muestra `price_subtotal`, con lo que cuadra exactamente con
  base/IVA/total; no aplicar redondeo monetario por línea (rompería el cuadre). La
  precisión «Product Price» ya no afecta al Importe (solo a los decimales de Precio U
  y Neto).
* **Anticipos (downpayments):** si RYP usara anticipos con precio, revisar el `t-if` de
  `td_net` y el contenido de `td_subtotal` para esas líneas (el `td_net` de la factura no
  filtra anticipos hoy).
* **Cambios de moneda:** ya soportado vía `display_currency` (`doc.currency_id` en el
  pedido, `o.currency_id` en la factura).
* **Inmunización frente a `sale_layout_category_hide_detail` (OCA):** si ambos módulos
  llegaran a coexistir en la misma base de datos, replicar en el `span` nuevo de la
  columna "Importe" del pedido el
  `t-if="not current_section or current_section.show_line_amount"` del OCA dejaría el
  render inmunizado frente al orden de herencia. Descartado por ahora: `current_section`
  es una variable del template de ese módulo (no instalado) y replicarla añadiría riesgo
  sin necesidad actual; cualquier implementación futura debe verificar el render con
  ambos órdenes de aplicación.
* **Nuevas herencias de terceros en la factura:** si un futuro módulo anclara en
  `td_subtotal` de `account.report_invoice_document` (además de
  `account_invoice_report_grouped_by_picking`), auditar de nuevo la estrategia de
  ocultación por `style` frente a `t-if` y la condición negada del span de "Importe".

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-20 | Versión inicial (columnas del informe de pedido) |
| 18.0.1.1.0 | 2026-10-20 | Añade el informe de factura (`account.report_invoice_document`): columna "Neto", sustitución del valor de «Importe» con cálculo propio sin impuestos (con coexistencia con la agrupación por albarán), y cabeceras "Precio U" en pedido y factura. Nueva dependencia `klo_invoice_report_price_unit_untaxed` y fichero `report/account_report_templates.xml` |
| 18.0.2.0.0 | 2026-10-22 | Campo computado price_unit_net (Neto = price_unit_untaxed × (1 − Dto/100), sin redondeo) renderizado con t-field con los mismos decimales que el formulario (precisión «Product Price»); Importe calculado desde Neto sin redondeos intermedios, cuadrado con la base del documento |
| 18.0.2.1.0 | 2026-10-22 | Importe = price_subtotal (cuadre exacto con base/IVA/total); Cantidad × Neto podía diferir ±0,01 € con impuestos precio incluido |
| 18.0.2.2.0 | 2026-10-22 | Separación de 1 mm (padding-left) entre las columnas numéricas del cuerpo en pedido y factura |
