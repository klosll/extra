# KLO — Factura Matricial (klo_factura_matricial)

> Documento técnico del módulo, orientado a futuros ajustes por IA o desarrolladores.

---

## Módulo

| Campo            | Valor                                              |
|------------------|----------------------------------------------------|
| Nombre técnico   | `klo_factura_matricial`                            |
| Nombre legible   | KLO - Factura Matricial                            |
| Versión          | `18.0.1.0.0`                                       |
| Autor            | KLO Ingeniería Informática S.L.L.                  |
| Licencia         | AGPL-3                                             |
| Categoría        | Accounting/Accounting                              |
| Dependencias     | `account`                                          |
| Ubicación        | `extra-addons/klo/extra/klo_factura_matricial`     |
| Fecha creación   | 2026-10-14                                         |
| Odoo versión     | 18.0 Community                                     |

---

## Descripción

Report QWeb **"Factura Matricial"** para `account.move` pensado para imprimir en
**impresora matricial sobre papel continuo** (279 mm alto × 210 mm ancho,
portrait, márgenes 0) con un **formulario preimpreso**: los datos se imprimen en
**posiciones fijas (mm)** en lugar de fluir como en la factura estándar.

La plantilla hereda de `account.report_invoice_document` con `primary="True"`
para reutilizar el contexto de datos y la lógica condicional de la factura
(`o` = `account.move`, `lang`, `docs`), sustituyendo únicamente el layout
(`web.external_layout`) por el layout de posiciones fijas.

Características:

- **Cabecera repetida en todas las hojas** (nº factura, referencia de cliente,
  dirección, fecha, NIF/CIF).
- **Cuerpo paginado**: máximo 15 líneas de detalle por hoja, desde 105 mm con
  interlineado de 6 mm.
- **Pie/totales solo en la última hoja** (base imponible, etiqueta e importe de
  impuestos, total, plazo de pago).
- Fuente monoespaciada Courier New 11px, márgenes 0, sin cabecera de compañía.

---

## Campo(s) añadido(s)

Ninguno. El módulo no añade campos ni modifica modelos de datos: solo define un
`ir.actions.report`, un `report.paperformat`, plantillas QWeb y un
`AbstractModel` de reporte.

---

## Dependencias

- **Odoo**: `account`
  - Plantilla heredada: `account.report_invoice_document`.
  - AbstractModel padre: `report.account.report_invoice`.
  - Grupos: `account.group_account_invoice`, `account.group_account_readonly`.
- Sin dependencias de otros módulos `klo_*`, OCA o externos.

---

## Lógica

### AbstractModel `report.klo_factura_matricial.report_factura_matricial`

Fichero `models/report.py`. Hereda de `report.account.report_invoice`
(`_inherit`) sin añadir métodos: reutiliza `_get_report_values` del reporte
estándar de facturas (`doc_ids`, `doc_model`, `docs`, `qr_code_urls`). El nombre
del modelo (46 chars) queda por debajo del límite de 63 de PostgreSQL, por lo
que no necesita `_table`.

### Plantilla `report_factura_matricial_document` (heredada, primary="True")

- Sustituye por completo `//t[@t-call='web.external_layout']`
  (`position="replace"`) y re-añade dentro del reemplazo los `t-set` que estaban
  dentro del t-call sustituido: `o = o.with_context(lang=lang)` y `forced_vat`.
- **Ordenación de líneas**: la MISMA que la plantilla base:
  `o.invoice_line_ids.sorted(key=lambda l: (-l.sequence, l.date, l.move_name, -l.id), reverse=True)`.
- **Paginación**: `line_pages = [lines[i:i+15] for i in range(0, len(lines), 15)] or [[]]`.
  Cada hoja es un `div.page` de 210×279 mm con `position:relative` y
  `overflow:hidden`. `page-break-after:always` salvo en la última hoja
  (`auto`, variable `page_lines_last` del `t-foreach`) para evitar una hoja en
  blanco final.
- **Cuerpo**: `t-foreach="page_lines" t-as="line"` con
  `line_y = 105 + line_index * 6` (mm). Las columnas numéricas (quantity,
  price_unit, price_subtotal) solo se imprimen si `line.display_type ==
  'product'`; secciones y notas solo imprimen `name`.
- **Impuestos de línea**: `', '.join([(tax.invoice_label or tax.name) for tax
  in line.tax_ids])` (misma expresión que la plantilla base).
- **Pie** (solo si `page_lines_last`): la etiqueta de impuestos se calcula
  desde `o.tax_totals` con las claves v18, uniendo todos los
  `subtotal['tax_groups'][]['group_name']` con `', '`.
- `t-field` para campos con formato (Monetary: amount_untaxed, amount_tax,
  amount_total, price_unit, price_subtotal; Date: invoice_date; Many2one:
  invoice_payment_term_id) siempre sobre elementos reales (`div`, `address`),
  nunca sobre nodos `<t>`. `t-esc` para texto plano (name, partner_id.ref,
  partner_id.vat, etiquetas de impuestos). `t-options` se evalúa como
  **expresión Python**, no como JSON: usar `"no_marker": True`.

### Posiciones (mm, top/left)

**Cabecera** (todas las hojas):

| Campo                                       | top | left | ancho | extra                     |
|---------------------------------------------|-----|------|-------|---------------------------|
| `o.name` (nº factura, t-esc)                | 63  | 20   | 52    |                           |
| `o.partner_id.ref` (t-esc)                  | 63  | 75   | 35    |                           |
| `o.partner_id` (contact, t-field)           | 50  | 115  | 90    | widget contact address+name |
| `o.invoice_date` (t-field)                  | 80  | 20   | 52    |                           |
| `o.partner_id.vat` (t-esc)                  | 80  | 75   | 35    |                           |

**Cuerpo** (top = 105 + índice×6, máx. 15 líneas por hoja):

| Campo                                        | left | ancho | alineación                    |
|----------------------------------------------|------|-------|-------------------------------|
| `line.name` (t-field widget text)            | 20   | 100   | izq., nowrap, oculta desborde |
| `line.quantity` (t-field)                    | 123  | 16    | dcha.                         |
| `line.price_unit` (t-field)                  | 140  | 16    | dcha.                         |
| etiquetas `line.tax_ids` (t-esc)             | 158  | 16    | izq., nowrap                  |
| `line.price_subtotal` (t-field)              | 175  | 30    | dcha.                         |

**Pie** (solo última hoja):

| Campo                                              | top | left | ancho |
|----------------------------------------------------|-----|------|-------|
| `o.amount_untaxed` (t-field)                       | 242 | 25   | 66    |
| etiqueta impuestos (`group_name`, t-esc)           | 242 | 93   | 16    |
| `o.amount_tax` (t-field)                           | 242 | 110  | 58    |
| `o.amount_total` (t-field)                         | 242 | 170  | 35    |
| `o.invoice_payment_term_id` (t-field)              | 265 | 20   | 90    |

Los anchos son fijos para evitar solapes entre columnas contiguas; el pie se
imprime alineado a la izquierda en las posiciones exactas del formulario.

---

## Vistas modificadas

Ninguna vista de backend se modifica. El módulo añade:

- `report.paperformat` `paperformat_factura_matricial`: `format=custom`,
  `page_width=210`, `page_height=279`, Portrait, márgenes 0,
  `header_line=False`, `header_spacing=0`, `dpi=80`.
- Plantilla QWeb heredada `report_factura_matricial_document`
  (`inherit_id="account.report_invoice_document"`, `primary="True"`).
- Plantilla raíz `report_factura_matricial`: `web.html_container` + foreach
  `docs` + `t-set lang` + `t-call` al documento heredado con `t-lang`.
- `ir.actions.report` `action_report_factura_matricial`: "Factura Matricial",
  `qweb-pdf`, binding (`binding_type=report`) en el formulario de `account.move`
  para los grupos `account.group_account_invoice` y
  `account.group_account_readonly`;
  `print_report_name = (object.name or 'Factura Matricial').replace('/', '-')`.

---

## Estructura de archivos

```
klo_factura_matricial/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── report.py                       # AbstractModel del reporte
├── report/
│   └── report_factura_matricial.xml    # paperformat + plantillas QWeb
├── views/
│   └── report_action.xml               # ir.actions.report
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Instalación / Actualización

```bash
# Instalar
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -i klo_factura_matricial \
    --stop-after-init

# Actualizar (tras cambios en plantillas o acción)
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_factura_matricial \
    --stop-after-init
```

La base de datos activa se lee de `db_name` en `config/odoo.conf`.

Disponible en el menú **Imprimir → Factura Matricial** del formulario de
facturas (`account.move`), para los grupos de contabilidad.

---

## Posibles adaptaciones futuras

- **Ajuste de posiciones**: los mm están hardcodeados en los `style` /
  `t-att-style` de la plantilla; ajustar directamente según el formulario
  preimpreso real (las tablas de posiciones de arriba sirven de guía).
- **Líneas por hoja / interlineado**: `max_lines` (15) y el cálculo
  `105 + line_index * 6` son los únicos puntos a tocar.
- **Impresión HTML en lugar de PDF**: cambiar `report_type` a `qweb-html` en
  `views/report_action.xml` si se prefiere imprimir desde el navegador.
- **Campos adicionales**: añadir nuevos divs absolutos dentro de los bloques de
  cabecera/cuerpo/pie; mantener `t-field` sobre elementos reales y `t-esc`
  para texto plano.
- **Descuentos / columnas extra**: el formulario no imprime descuentos; si se
  necesitan, añadir columna siguiendo el patrón de `price_unit`.
- Si un módulo tercero hereda `account.report_invoice_document` con xpaths
  sobre nodos interiores, su diff también se aplicará a esta variante primary
  salvo que sus xpaths dejen de encontrar los nodos sustituidos
  (comportamiento estándar de herencia primary).

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-14 | Versión inicial        |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
