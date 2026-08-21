# KLO — Invoice Dot Matrix Report

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_invoice_matrix` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_invoice_matrix/` |

---

## Descripción funcional

Añade un **informe de factura QWeb optimizado para impresoras matriciales** (punto-matriz). El informe hereda el documento estándar de factura de Odoo (`account.report_invoice_document`) y le inyecta estilos CSS para forzar tipografía monoespaciada (`Courier New`), tamaño de fuente reducido (10 px) y padding compacto en tablas. Se define además un formato de papel personalizado con dimensiones y márgenes adecuados para papel de impresora matricial.

---

## Lógica (sin campos ni métodos nuevos)

El módulo **no añade campos ni sobrescribe métodos Python**. Toda la lógica reside en:

1. **Formato de papel** (`data/report_paperformat_data.xml`): registro `report.paperformat` con página personalizada 280×219 mm, márgenes reducidos, DPI 90 y `disable_shrinking=True`.
2. **Plantilla QWeb principal** (`reports/invoice_report_templates.xml`): define `invoice_report_dot_matrix` (envoltorio que itera `docs`) y la acción `ir.actions.report` vinculada al modelo `account.move`, con `binding_type="report"` (aparece en el menú de impresión de facturas).
3. **Herencia del documento de factura** (`reports/report_invoice.xml`): plantilla `invoice_report_dot_matrix_document` con `primary="True"` que hereda `account.report_invoice_document` e inyecta un bloque `<style>` antes del contexto de idioma, forzando:
   - `font-size: 10px` en todo el documento (`body, body *`)
   - `padding: 1px` en celdas de tabla
   - Títulos proporcionales: `h1` 12 px, `h2` 10 px, `h3` 9 px
   - `font-family: 'Courier New', monospace` y `line-height: 1.2`

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` | Modelo `account.move` y plantilla base `account.report_invoice_document` que se hereda |

No depende de módulos externos fuera del núcleo.

---

## Vistas / Plantillas modificadas

### Formato de papel (datos)

| Registro | Modelo | Detalle |
|---|---|---|
| `paperformat_dot_matrix_printer_invoice_reports` | `report.paperformat` | `noupdate=1`. Página custom 280×219 mm, orientación Portrait, márgenes top 30 / bottom 27 / left 7 / right 7, `header_line=False`, `header_spacing=43`, `dpi=90`, `disable_shrinking=True`. |

### Plantilla QWeb envoltorio + acción de informe

| Registro | Tipo | Detalle |
|---|---|---|
| `invoice_report_dot_matrix` | QWeb template | Envoltorio que itera `docs`, fija el idioma del partner y llama al documento principal. |
| `action_report_sale_invoice_dot_matrix` | `ir.actions.report` | Nombre "Invoices (Dot Matrix)", modelo `account.move`, tipo `qweb-pdf`, vinculado al modelo (`binding_model_id`), usa el paperformat del módulo. |

### Herencia del documento de factura

| Atributo | Valor |
|---|---|
| **Plantilla heredada** | `account.report_invoice_document` |
| **Modo** | `primary="True"` |
| **XPath** | `//t[@t-set='o'][@t-value='o.with_context(lang=lang)']` posición `before` |
| **Cambio** | Inyecta bloque `<style>` con CSS para fuente monoespaciada y tamaño reducido |

---

## Estructura de archivos

```
klo_report_invoice_matrix/
├── __init__.py                      ← Vacío (sin modelos Python)
├── __manifest__.py
├── data/
│   └── report_paperformat_data.xml  ← Paperformat matricial 280×219 mm
├── models/
│   └── __init__.py                  ← Vacío
├── reports/
│   ├── invoice_report_templates.xml ← Plantilla QWeb + acción ir.actions.report
│   └── report_invoice.xml           ← Hereda account.report_invoice_document (primary)
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_invoice_matrix --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_invoice_matrix --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Parametrizar el tamaño de fuente mediante un `ir.config_parameter` (como hace `klo_report_layout_small_font_header`) en lugar de fijarlo a 10 px en el CSS.
- Ajustar las dimensiones del paperformat si se cambia de formato de papel continuo a hojas sueltas.
- Añadir una variante para abonos (`out_refund`) con cabecera diferenciada si el cliente lo requiere.
