# KLO — Precio unitario con impuestos en líneas de pedido de venta

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_price_unit_with_tax` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales/Sales |
| **Dependencias** | `sale` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_price_unit_with_tax/` |

## Descripción funcional

Añade un campo **Precio unitario con impuestos** en las líneas del pedido de venta, calculado a partir del precio unitario, los impuestos, el descuento y la moneda. Se muestra junto al campo estándar `price_unit` tanto en la vista formulario como en la lista embebida de líneas, de forma que el comercial vea de inmediato el coste final por unidad impuestos incluidos.

## Campo(s) añadido(s) o lógica

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `sale.order.line` | `price_unit_with_tax` | `Monetary` (`currency_field='currency_id'`) | `Unit Price with Tax` | `compute='_compute_price_unit_with_tax'`, `store=True`, `readonly=True`. Help: "Unit price including taxes". |

### Método `_compute_price_unit_with_tax`

- Decorador: `@api.depends('price_unit', 'tax_id', 'product_uom_qty', 'discount', 'order_id.partner_id')`.
- Para cada línea:
  - Si `product_uom_qty` es distinto de cero: prepara una `base_line` con `line._prepare_base_line_for_taxes_computation()`, añade los detalles de impuestos con `account.tax._add_tax_details_in_base_line(base_line, line.company_id)`, y calcula `price_total = base_line['tax_details']['raw_total_included_currency']`; el campo resulta `price_total / product_uom_qty`.
  - Si no hay cantidad: toma directamente `line.price_unit` como valor.

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` (Odoo core) | Provee `sale.order.line`, los métodos de cálculo de impuestos (`_prepare_base_line_for_taxes_computation`) y la vista `sale.view_order_form`. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

| Vista heredada | XPath | Cambio |
|---|---|---|
| `sale.view_order_form` (`sale.order.form`) | `//field[@name='order_line']/form//field[@name='price_unit']` `position="after"` | Añade `price_unit_with_tax` en el formulario embebido de línea. |
| `sale.view_order_form` (`sale.order.form`) | `//field[@name='order_line']/list//field[@name='price_unit']` `position="after"` | Añade la columna `price_unit_with_tax` con `optional="show"` en la lista embebida de líneas. |

## Estructura de archivos

```
klo_price_unit_with_tax/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line.py   ← _inherit de sale.order.line + compute
├── views/
│   └── sale_order_views.xml ← Hereda view_order_form (form + list)
├── tests/
│   └── test_module.py
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_price_unit_with_tax --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_price_unit_with_tax --stop-after-init
```

## Posibles adaptaciones futuras

- Extender el cálculo a líneas de factura (`account.move.line`) reutilizando la misma lógica de `base_line`.
- Hacer el campo no almacenado (`store=False`) si se quiere evitar recompute masivo en pedidos históricos.
- Añadir un campo complementario "precio total con impuestos por línea" para mostrar ambos en la vista.
