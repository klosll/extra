# KLO — Account Invoice Triple Discount (Improvement)

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_account_invoice_triple_discount` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | QubiQ, Tecnativa, GRAP, Odoo Community Association (OCA), KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting & Finance |
| **Dependencias** | `account_invoice_triple_discount` (OCA) |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_account_invoice_triple_discount/` |

---

## Descripción funcional

Mejora el informe de factura del módulo OCA `account_invoice_triple_discount` para que las **tres columnas de descuento** (`discount1`, `discount2`, `discount3`) se muestren de forma independiente en la tabla del informe, en lugar de la única columna `discount` estándar de Odoo. Cada columna solo aparece si alguna línea del informe tiene ese descuento aplicado.

---

## Campo(s) añadido(s) o lógica

No añade campos ni métodos Python (los campos `discount1`, `discount2`, `discount3` los provee el módulo OCA base en `account.move.line`). Toda la lógica es de presentación en el template QWeb:

- `display_discount = False` (oculta la columna de descuento único de Odoo).
- `display_discount1/2/3 = any(l.discountN for l in o.invoice_line_ids)` (muestra cada columna solo si hay al menos una línea con ese descuento).
- `discount_class = 'text-end %s' % ('d-none d-md-table-cell' if report_type == 'html' else '')` (clase responsive para HTML).

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account_invoice_triple_discount` (OCA) | Provee los campos `discount1`, `discount2`, `discount3` en `account.move.line` y la lógica de cálculo de los tres descuentos encadenados. |

El módulo OCA reside en los repositorios de OCA (ruta `extra-addons/oca/` del proyecto).

---

## Vistas modificadas

### Template `account.report_invoice_document`

| Vista base heredada | XPath | Acción |
|---|---|---|
| `account.report_invoice_document` (template `klo_report_invoice_document`, `priority="100"`) | `//t[@t-set='display_discount']` `position="attributes"` | Fuerza `t-value=False` para ocultar la columna de descuento único. |
| `account.report_invoice_document` | `//t[@t-set='display_discount']` `position="after"` | Define `display_discount1/2/3` y `discount_class`. |
| `account.report_invoice_document` | `//th[@name='th_discount']` `position="attributes"` | Aplica `style="visibility: hidden;"` a la cabecera de descuento único. |
| `account.report_invoice_document` | `//th[@name='th_discount']` `position="after"` | Añade tres `<th>` (`th_discount1/2/3`) condicionales con etiquetas "Disc.1 %", "Disc.2 %", "Disc.3 %". |
| `account.report_invoice_document` | `//td[span[@t-field='line.discount']]` `position="attributes"` | Aplica `style="visibility: hidden;"` a la celda de descuento único. |
| `account.report_invoice_document` | `//td[span[@t-field='line.discount']]` `position="after"` | Añade tres `<td>` condicionales con `t-field="line.discount1/2/3"`. |

---

## Estructura de archivos

```
klo_account_invoice_triple_discount/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py            ← Vacío (sin modelos propios)
├── report/
│   └── invoice.xml            ← Hereda account.report_invoice_document
└── static/description/
    ├── icon.png
    └── Technical_context.md   ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_account_invoice_triple_discount --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_account_invoice_triple_discount --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`. Requiere que el módulo OCA `account_invoice_triple_discount` esté disponible en el `addons_path`.

---

## Posibles adaptaciones futuras

- Sustituir `visibility: hidden;` por `position="replace"` para eliminar del DOM la columna de descuento único en lugar de solo ocultarla.
- Añadir totales o subtotales por descuento en el pie del informe.
- Replicar el mismo patrón de tres columnas en el informe de pedido de venta (`sale.report_saleorder_document`).
