# KLO — Ocultar fecha límite del pedido en RFQ

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_rfq_hide_order_deadline` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_rfq_hide_order_deadline/` |

## Descripción funcional

Oculta la **Fecha límite del pedido** (*Order Deadline*) de la cabecera del informe QWeb de **Pedido de compra** mientras el documento siga siendo una **Solicitud de presupuesto** (RFQ) sin confirmar (estados `draft`, `sent` o `to approve`).

Una vez confirmado el pedido (estados `purchase`, `done` o `cancel`), el campo *Order Deadline* se muestra con normalidad.

El bloque *Order Deadline* no existe en la plantilla `purchase.report_purchasequotation_document`, por lo que la modificación se aplica únicamente a:

- **Purchase Order** (`purchase.report_purchaseorder_document`).

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica se implementa mediante herencia QWeb.

El módulo modifica el atributo `t-elif` del bloque de la fecha límite en la plantilla base para que no se renderice mientras el documento sea una RFQ:

```qweb
<div t-elif="o.date_order and o.state not in ('draft', 'sent', 'to approve')" class="col-2 bm-2">
    <strong>Order Deadline:</strong>
    <p t-field="o.date_order" t-options="{'date_only': 'true'}" class="m-0"/>
</div>
```

De este modo, el `<div>` de *Order Deadline* se oculta únicamente en estados RFQ, manteniendo intacta la cadena `if/elif` con el bloque *Order Date* anterior.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee la plantilla base `purchase.report_purchaseorder_document`, que contiene el bloque de la fecha límite en la cabecera. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchaseorder_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_order_report_hide_order_deadline` | `//div[@t-elif='o.date_order']` | `attributes` | Reemplaza el `t-elif` por `o.date_order and o.state not in ('draft', 'sent', 'to approve')`. |

## Estructura de archivos

```
klo_purchase_rfq_hide_order_deadline/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py          ← Vacío (sin modelos)
├── reports/
│   └── purchase_order_report.xml   ← Hereda purchase.report_purchaseorder_document
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
  -d topapro_dev -i klo_purchase_rfq_hide_order_deadline --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_rfq_hide_order_deadline --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o tipo de pedido en lugar de aplicarlo de forma global.
- Sustituir la condición fija por un campo funcional (p. ej. `o.company_id.hide_order_deadline_in_rfq`) para permitir activar/desactivar el comportamiento por compañía.
- Extender la misma lógica a otros informes de compra que incluyan la fecha límite del pedido.
