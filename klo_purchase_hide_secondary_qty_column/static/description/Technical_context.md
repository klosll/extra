# KLO — Ocultar columna "Segunda Ctd" en informes de compra

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_hide_secondary_qty_column` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase`, `purchase_order_secondary_unit` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_hide_secondary_qty_column/` |

## Descripción funcional

Oculta siempre la columna **Segunda Ctd** (*Second Qty*) de los informes QWeb de compra, tanto en el **Pedido de compra** confirmado (PO) como en la **Solicitud de presupuesto** (RFQ).

La columna es añadida por el módulo OCA `purchase_order_secondary_unit` en las plantillas:

- `purchase.report_purchaseorder_document`
- `purchase.report_purchasequotation_document`

Este módulo no elimina los elementos, sino que les aplica `t-if="False"` para que no se rendericen en ningún estado del documento.

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` solo contiene la cabecera de copyright). Toda la lógica se implementa mediante herencia QWeb.

El módulo añade el atributo `t-if="False"` a las celdas de cabecera (`<th>`) y contenido (`<td>`) de la columna *Second Qty*:

```qweb
<!-- Pedido de compra (PO) -->
<th name="th_secondary_unit" class="text-end" t-if="False">
    <strong>Second Qty</strong>
</th>
<td id="secondary_unit" class="text-end" t-if="False">...</td>

<!-- Solicitud de presupuesto (RFQ) -->
<th name="secondary_unit" class="text-end" t-if="False">
    <strong>Second Qty</strong>
</th>
<td id="secondary_unit" class="text-end" t-if="False">...</td>
```

De este modo, la columna completa deja de renderizarse en ambos informes sin modificar la estructura original de las plantillas.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee las plantillas base `purchase.report_purchaseorder_document` y `purchase.report_purchasequotation_document`. |
| `purchase_order_secondary_unit` (OCA) | Añade la columna *Second Qty* que este módulo oculta. Se declara como dependencia para garantizar que sus elementos `<th>` y `<td>` existan cuando se apliquen los `xpath` de esta herencia. |

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchaseorder_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_hide_secondary_qty_order` | `//th[@name='th_secondary_unit']` | `attributes` | Añade `t-if="False"`. |
| `klo_purchase_hide_secondary_qty_order` | `//td[@id='secondary_unit']` | `attributes` | Añade `t-if="False"`. |

### Plantilla heredada: `purchase.report_purchasequotation_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_hide_secondary_qty_quotation` | `//th[@name='secondary_unit']` | `attributes` | Añade `t-if="False"`. |
| `klo_purchase_hide_secondary_qty_quotation` | `//td[@id='secondary_unit']` | `attributes` | Añade `t-if="False"`. |

## Estructura de archivos

```
klo_purchase_hide_secondary_qty_column/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py          ← Solo cabecera de copyright (sin modelos)
├── reports/
│   └── purchase_order_report.xml   ← Hereda las plantillas de compra
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
  -d topapro_dev -i klo_purchase_hide_secondary_qty_column --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_hide_secondary_qty_column --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o tipo de pedido en lugar de aplicarlo de forma global.
- Sustituir la condición fija `False` por un campo funcional (p. ej. `o.company_id.hide_secondary_uom_in_reports`) para permitir activar/desactivar el comportamiento por compañía.
- Aplicar la misma lógica a otros informes que incluyan la columna *Second Qty*.
