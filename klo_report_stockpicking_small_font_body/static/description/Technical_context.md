# KLO — Stock Picking Report Small Font Body

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_stockpicking_small_font_body` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `sale` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_stockpicking_small_font_body/` |

---

## Descripción funcional

Reduce el **tamaño de fuente del cuerpo del informe de albarán de entrega** (`stock.report_delivery_document`) para una impresión más compacta en papel continuo. Se auto-crea el parámetro de sistema `klo.stockpicking_report_small_font_body` con valor `10` (px) por defecto, ajustable desde *Parámetros del sistema*. Define además un formato de papel "Continuous paper" (219×280 mm) y reemplaza el `<h2>` del título por un `<div class="document-title">`.

> **Nota:** el `__manifest__.py` declara como dependencia `sale` (no `stock`); el template heredado `stock.report_delivery_document` está disponible de forma transitiva.

---

## Campo(s) añadido(s) o lógica

No añade campos ni métodos Python. Toda la lógica es declarativa:

1. **`ir.config_parameter`** `klo.stockpicking_report_small_font_body` = `10` (`noupdate="1"`, `forcecreate="False"`).
2. **`report.paperformat`** "Continuous paper": formato `custom` 219×280 mm, márgenes 45/27/7/7, DPI 90, `disable_shrinking=True`, marcado como `default`.
3. **Template QWeb** lee el parámetro y aplica:
   - `font-size: <valor>px !important` a `body, body *`
   - `padding: 1px` a `.table th, .table td`
   - Títulos proporcionales: `h1` = 1.5×, `h2` = 1.25×, `h3` = 1.125×
   - Fuente monoespaciada `'Courier New', monospace` y `line-height: 1.2`
   - `.document-title` con tamaño 1.5×
   - Reemplaza el `<h2>` del título por un `<div class="document-title">` con `t-field="o.name"`.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` | Dependencia declarada en el manifest (provee disponibilidad del entorno de informes). |
| `stock` (transitivo) | Provee el template `stock.report_delivery_document` que se hereda. |

No depende de módulos OCA ni externos.

---

## Vistas modificadas

### Template `stock.report_delivery_document`

| Vista base heredada | XPath | Acción |
|---|---|---|
| `stock.report_delivery_document` (template `klo_report_delivery_document_small_font_body`) | `//t[@t-set='o'][@t-value="o.with_context(lang=o._get_report_lang())"]` `position="before"` | Inyecta `<style>` con el tamaño de fuente dinámico leído del parámetro de sistema. |
| `stock.report_delivery_document` | `//h2` `position="replace"` | Sustituye el `<h2>` por un `<div class="document-title">` con `<span t-field="o.name">` (ej. `WH/OUT/0001`). |

---

## Estructura de archivos

```
klo_report_stockpicking_small_font_body/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── ir_config_parameter_data.xml   ← Crea klo.stockpicking_report_small_font_body = 10
│   └── report_paperformat_data.xml    ← Crea paperformat "Continuous paper"
├── models/
│   └── __init__.py                    ← Vacío (sin modelos)
├── reports/
│   └── report_deliveryslip.xml        ← Hereda stock.report_delivery_document
└── static/description/
    ├── icon.png
    └── Technical_context.md          ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_stockpicking_small_font_body --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_stockpicking_small_font_body --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Cambiar la dependencia del manifest de `sale` a `stock` para reflejar con precisión la dependencia real del template heredado.
- Generalizar el patrón de "small font body" a un módulo base reutilizable del que hereden los informes de pedido, albarán y factura.
- Hacer el formato de papel "Continuous paper" no `default` para evitar afectar a informes que no lo requieran.
