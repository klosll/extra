# KLO — Ocultar comprador en informe de compra

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_rfq_hide_buyer` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_rfq_hide_buyer/` |

## Descripción funcional

Oculta el **Comprador** (*Buyer*) de la cabecera del informe QWeb de **Pedido de compra** en **todos los estados** del documento, tanto mientras es una **Solicitud de presupuesto** (RFQ) como una vez confirmado el pedido (estados `purchase` o `done`).

El campo *Buyer* no existe en la plantilla `purchase.report_purchasequotation_document`, por lo que la modificación se aplica únicamente a:

- **Purchase Order** (`purchase.report_purchaseorder_document`).

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica se implementa mediante herencia QWeb.

El módulo modifica el atributo `t-if` del bloque del comprador en la plantilla base para que nunca se renderice:

```qweb
<div t-if="False" class="col">
    <strong>Buyer</strong>
    <div t-field="o.user_id"/>
</div>
```

De este modo, el `<div>` del comprador se oculta independientemente del estado del documento.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee la plantilla base `purchase.report_purchaseorder_document`, que contiene el bloque del comprador en la cabecera. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchaseorder_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_order_report_hide_buyer` | `//div[@t-if='o.user_id']` | `attributes` | Reemplaza el `t-if` por `False`. |

## Estructura de archivos

```
klo_purchase_rfq_hide_buyer/
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
  -d topapro_dev -i klo_purchase_rfq_hide_buyer --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_rfq_hide_buyer --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía o tipo de pedido en lugar de aplicarlo de forma global.
- Sustituir la condición fija por un campo funcional (p. ej. `o.company_id.hide_buyer_in_report`) para permitir activar/desactivar el comportamiento por compañía.
- Extender la misma lógica a otros informes de compra que incluyan el comprador.
