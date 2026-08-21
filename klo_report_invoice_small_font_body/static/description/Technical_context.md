# KLO — Factura con cuerpo de fuente pequeña

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_invoice_small_font_body` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_invoice_small_font_body/` |

## Descripción funcional

Compacta el informe de factura reduciendo el tamaño de fuente del cuerpo para permitir impresión más densa (p. ej. papel continuo). El tamaño se controla mediante un **parámetro de sistema** y se aplica con CSS `!important` a todo el documento, con tamaños proporcionales para títulos. Además define un **formato de papel continuo** (280×219 mm) y reemplaza el título del documento por un bloque con clase `document-title`.

> **Nota de fidelidad al código:** el `__manifest__.py` menciona el parámetro `klo.invoice_report_body_small_font` con valor 8, pero el código real usa la clave `klo.invoice_report_small_font_body`, el dato XML la inicializa a `10` y la plantilla usa `'8'` como fallback por defecto.

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica es declarativa:

- **Parámetro de sistema** `ir.config_parameter` con clave `klo.invoice_report_small_font_body` y valor `10` (registro `noupdate="1"`, `forcecreate="False"`).
- **Formato de papel** `report.paperformat` externo id `paperformat_continuous_paper`, nombre "Continuous paper", `default=True`, formato `custom` 280×219 mm, márgenes (top 45, bottom 27, left/right 7), `header_spacing=43`, `dpi=90`, `disable_shrinking=True`.
- **Plantilla QWeb** que inyecta un `<style>` con `font-size` dinámico leído del parámetro.

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` (Odoo core) | Provee la plantilla base `account.report_invoice_document` y el modelo `report.paperformat`. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

Plantilla heredada: `account.report_invoice_document` (id `klo_invoice_report_small_font_body`).

| XPath | Posición | Cambio |
|---|---|---|
| `//t[@t-set='o'][@t-value='o.with_context(lang=lang)']` | `before` | Inyecta `t-set="font_size"` leyendo `ir.config_parameter` `klo.invoice_report_small_font_body` (default `'8'`) y un bloque `<style>` que fuerza `font-size` en `body, body *`, padding `1px` en `.table th/td`, tamaños proporcionales para `h1`/`h2`/`h3`, fuente monoespaciada `Courier New` y tamaño `1.5×` para `.document-title`. |
| `//t[@t-set='layout_document_title']` | `replace` | Reemplaza el título por un `<div class="document-title">` con las etiquetas de tipo de documento (Invoice, Draft Invoice, Credit Note, Vendor Bill, etc.) y el `t-field="o.name"`. |

## Estructura de archivos

```
klo_report_invoice_small_font_body/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── ir_config_parameter_data.xml   ← Parámetro klo.invoice_report_small_font_body=10
│   └── report_paperformat_data.xml    ← Paperformat "Continuous paper"
├── models/
│   └── __init__.py                    ← Vacío (sin modelos)
├── reports/
│   └── report_invoice.xml             ← Hereda account.report_invoice_document
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_invoice_small_font_body --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_invoice_small_font_body --stop-after-init
```

## Posibles adaptaciones futuras

- Alinear la descripción del `__manifest__.py` con la clave real del parámetro y el valor por defecto para evitar la discrepancia documentada.
- Convertir el `<style>` inyectado en un asset CSS cargado por `web.assets_common` para mejorar el renderizado en wkhtmltopdf.
- Parametrizar también la familia tipográfica y el interlineado vía `ir.config_parameter` en lugar de fijarlos en la plantilla.
