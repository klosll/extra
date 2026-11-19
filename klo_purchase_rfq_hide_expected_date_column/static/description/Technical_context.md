# KLO — Ocultar columna "Fecha prevista" en la solicitud de presupuesto (RFQ)

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_rfq_hide_expected_date_column` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_rfq_hide_expected_date_column/` |

## Descripción funcional

Oculta siempre la columna **Fecha prevista** (*Expected Date*) del informe QWeb de **Solicitud de presupuesto** (RFQ).

La columna es añadida por el módulo `purchase` de Odoo core en la plantilla:

- `purchase.report_purchasequotation_document`

Este módulo no elimina los elementos, sino que les aplica `t-if="False"` para que no se rendericen en ningún estado del documento.

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` solo contiene la cabecera de copyright). Toda la lógica se implementa mediante herencia QWeb.

El módulo añade el atributo `t-if="False"` a las celdas de cabecera (`<th>`) y contenido (`<td>`) de la columna *Expected Date*:

```qweb
<!-- Solicitud de presupuesto (RFQ) -->
<th name="th_expected_date" class="text-center" t-if="False">
    <strong>Expected Date</strong>
</th>
<td class="text-center" t-if="False">
    <span t-field="order_line.date_planned"/>
</td>
```

De este modo, la columna completa deja de renderizarse en el informe RFQ sin modificar la estructura original de la plantilla.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee la plantilla base `purchase.report_purchasequotation_document` y los elementos `<th>` y `<td>` de la columna *Expected Date* que este módulo oculta. |

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchasequotation_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_quotation_hide_expected_date` | `//th[@name='th_expected_date']` | `attributes` | Añade `t-if="False"`. |
| `klo_purchase_quotation_hide_expected_date` | `//td[span[@t-field='order_line.date_planned']]` | `attributes` | Añade `t-if="False"`. |

## Estructura de archivos

```
klo_purchase_rfq_hide_expected_date_column/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py          ← Solo cabecera de copyright (sin modelos)
├── reports/
│   └── purchase_order_report.xml   ← Hereda la plantilla RFQ de compra
├── static/
│   └── description/
│       ├── icon.png
│       └── Technical_context.md
└── .gitignore
```

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -i klo_purchase_rfq_hide_expected_date_column --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_rfq_hide_expected_date_column --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o tipo de pedido en lugar de aplicarlo de forma global.
- Sustituir la condición fija `False` por un campo funcional (p. ej. `o.company_id.hide_expected_date_in_rfq`) para permitir activar/desactivar el comportamiento por compañía.
- Aplicar la misma lógica al informe de pedido de compra confirmado (PO) si también se requiere ocultar la columna en ese documento.
