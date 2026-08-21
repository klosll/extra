# KLO — Sale Order Report Small Font Body

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_saleorder_small_font_body` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `sale` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_saleorder_small_font_body/` |

---

## Descripción funcional

Reduce el **tamaño de fuente del cuerpo del informe de pedido de venta** para lograr una impresión más compacta (pensado para papel continuo). Se auto-crea el parámetro de sistema `klo.saleorder_report_small_font_body` con valor `10` (px) por defecto, ajustable desde *Parámetros del sistema* sin tocar código. Además define un formato de papel "Continuous paper" (219×280 mm) y reemplaza el título del documento por uno propio con clase `.document-title`.

---

## Campo(s) añadido(s) o lógica

No añade campos ni métodos Python. Toda la lógica es declarativa:

1. **`ir.config_parameter`** `klo.saleorder_report_small_font_body` = `10` (`noupdate="1"`, `forcecreate="False"`).
2. **`report.paperformat`** "Continuous paper": formato `custom` 219×280 mm, márgenes 45/27/7/7, DPI 90, `disable_shrinking=True`, marcado como `default`.
3. **Template QWeb** lee el parámetro y aplica:
   - `font-size: <valor>px !important` a `body, body *`
   - `padding: 1px` a `.table th, .table td`
   - Títulos proporcionales: `h1` = 1.5×, `h2` = 1.25×, `h3` = 1.125×
   - Fuente monoespaciada `'Courier New', monospace` y `line-height: 1.2`
   - `.document-title` con tamaño 1.5×
   - Reemplaza `layout_document_title` por un `<div class="document-title">` con prefijo dinámico según estado (`Quotation #`, `Order #`, `Pro-Forma Invoice #`).

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` | Provee el template `sale.report_saleorder_document` que se hereda. |

No depende de módulos OCA ni externos.

---

## Vistas modificadas

### Template `sale.report_saleorder_document`

| Vista base heredada | XPath | Acción |
|---|---|---|
| `sale.report_saleorder_document` (template `klo_saleorder_report_small_font_body`) | `//t[@t-set='doc'][@t-value="doc.with_context(lang=doc.partner_id.lang)"]` `position="before"` | Inyecta `<style>` con el tamaño de fuente dinámico leído del parámetro de sistema. |
| `sale.report_saleorder_document` | `//t[@t-set='layout_document_title']` `position="replace"` | Sustituye el título por un `<div class="document-title">` con prefijo según `doc.state` (draft/sent → "Quotation #", proforma → "Pro-Forma Invoice #", resto → "Order #") seguido de `doc.name`. |

---

## Estructura de archivos

```
klo_report_saleorder_small_font_body/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── ir_config_parameter_data.xml   ← Crea klo.saleorder_report_small_font_body = 10
│   └── report_paperformat_data.xml    ← Crea paperformat "Continuous paper"
├── models/
│   └── __init__.py                    ← Vacío (sin modelos)
├── reports/
│   └── sale_order_templates.xml       ← Hereda sale.report_saleorder_document
└── static/description/
    ├── icon.png
    └── Technical_context.md          ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_saleorder_small_font_body --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_saleorder_small_font_body --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Generalizar el parámetro de tamaño de fuente a otros informes (facturas, albaranes) reutilizando el mismo patrón.
- Cambiar la fuente monoespaciada por una proporcional configurable vía otro parámetro de sistema.
- Hacer el formato de papel "Continuous paper" no `default` para no afectar a otros informes que no lo necesiten.
