# KLO — Ocultar dirección de envío en RFQ

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_rfq_hide_shipping_address` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_rfq_hide_shipping_address/` |

## Descripción funcional

Oculta la **Dirección de envío** (*Shipping address*) de la cabecera de los informes QWeb de Compra mientras el documento siga siendo una **Solicitud de presupuesto** (RFQ) sin confirmar, es decir, mientras `o.state` esté en `('draft', 'sent', 'to approve')`.

Una vez que el pedido de compra se confirma (estados `purchase` o `done`), la dirección de envío vuelve a mostrarse con normalidad.

Afecta a ambos informes:

- **Request for Quotation** (`purchase.report_purchasequotation_document`).
- **Purchase Order** (`purchase.report_purchaseorder_document`).

## Campo(s) añadido(s) o lógica

No añade campos ni modelos Python (`models/__init__.py` está vacío). Toda la lógica se implementa mediante herencia QWeb.

En lugar de modificar el atributo `t-if` del bloque de dirección de envío, el módulo **anula la variable `information_block`** justo antes del `<div class="page">` cuando el documento está en estado RFQ:

```qweb
<t t-if="o.state in ('draft', 'sent', 'to approve')">
    <t t-set="information_block" t-value="None"/>
</t>
```

`information_block` es la variable que el layout de informes utiliza para renderizar el bloque de dirección complementaria en la cabecera. Al asignarle `None`, se evita que se muestre cualquier dirección que haya sido establecida previamente en el mismo renderizado.

> **Nota:** El módulo `purchase_stock` añade un `<t t-else="">` inmediatamente después del `<t t-if="o.dest_address_id">` del template base, que rellena `information_block` con la dirección del almacén (*warehouse*). Si modificáramos directamente el `t-if` del bloque base para forzarlo a `False` en RFQ, se activaría ese `t-else` y aparecería la dirección del almacén. Por eso se opta por anular `information_block` de forma independiente, sin interferir en la lógica `t-if`/`t-else` de `purchase` ni de `purchase_stock`.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase` (Odoo core) | Provee las plantillas base `purchase.report_purchasequotation_document` y `purchase.report_purchaseorder_document`, que contienen el bloque de dirección de envío en la cabecera. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

### Plantilla heredada: `purchase.report_purchasequotation_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_quotation_report_hide_shipping_address` | `//div[@class='page']` | `before` | Inserta un `<t t-if="o.state in ('draft', 'sent', 'to approve')">` que anula `information_block` asignándole `None`. |

### Plantilla heredada: `purchase.report_purchaseorder_document`

| ID de la herencia | XPath | Posición | Cambio |
|---|---|---|---|
| `klo_purchase_order_report_hide_shipping_address` | `//div[@class='page']` | `before` | Inserta un `<t t-if="o.state in ('draft', 'sent', 'to approve')">` que anula `information_block` asignándole `None`. |

## Estructura de archivos

```
klo_purchase_rfq_hide_shipping_address/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py          ← Vacío (sin modelos)
├── reports/
│   └── purchase_order_report.xml   ← Hereda purchase.report_purchasequotation_document y purchase.report_purchaseorder_document
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
  -d topapro_dev -i klo_purchase_rfq_hide_shipping_address --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d topapro_dev -u klo_purchase_rfq_hide_shipping_address --stop-after-init
```

## Posibles adaptaciones futuras

- Hacer el ocultamiento configurable por compañía, almacén o tipo de operación en lugar de aplicarlo de forma global.
- Sustituir la condición estática por un campo funcional (p. ej. `o.company_id.hide_shipping_address_in_rfq`) para permitir activar/desactivar el comportamiento por compañía.
- Extender la misma lógica a otros informes de compra que incluyan la dirección de envío.
