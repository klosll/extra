# KLO — Ocultar llegada esperada en informe de Pedido de compra

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_rfq_hide_expected_arrival` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_rfq_hide_expected_arrival/` |

## Descripción funcional

Oculta la **Llegada esperada** (*Expected Arrival*) de la cabecera del informe QWeb de **Pedido de compra** en **todos los estados**, tanto en **Solicitud de presupuesto** (RFQ) como en **Pedido de compra confirmado**.

El bloque *Expected Arrival* no existe en la plantilla `purchase.report_purchasequotation_document`, por lo que la modificación se aplica únicamente a:

- **Purchase Order** (`purchase.report_purchaseorder_document`).

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica se implementa mediante herencia QWeb.

El módulo modifica el atributo `t-if` del bloque de la llegada esperada en la plantilla base para que nunca se renderice:

```qweb
<div t-if="False" class="col-2 bm-2">
    <strong>Expected Arrival:</strong>
    <p t-field="o.date_planned" t-options="{'date_only': 'true'}" class="m-0"/>
</div>
```

De este modo, el `<div>` de *Expected Arrival* se oculta siempre, en todos los estados del documento, sin afectar al resto de elementos de la cabecera del informe.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee la plantilla base `purchase.report_purchaseorder_document`, que contiene el bloque de la llegada esperada en la cabecera. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchaseorder_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_order_report_hide_expected_arrival` | `//div[@t-if='o.date_planned']` | `attributes` | Reemplaza el `t-if` por `False`. |

## Estructura de archivos

```
klo_purchase_rfq_hide_expected_arrival/
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
  -d topapro_dev -i klo_purchase_rfq_hide_expected_arrival --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_rfq_hide_expected_arrival --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o tipo de pedido en lugar de aplicarlo de forma global.
- Sustituir la condición fija por un campo funcional (p. ej. `o.company_id.hide_expected_arrival_in_po_report`) para permitir activar/desactivar el comportamiento por compañía.
- Extender la misma lógica a otros informes de compra que incluyan la llegada esperada en la cabecera.
