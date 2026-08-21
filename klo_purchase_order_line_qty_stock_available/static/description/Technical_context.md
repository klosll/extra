# KLO — Stock disponible en líneas de pedido de compra

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_purchase_order_line_qty_stock_available` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchases |
| **Dependencias** | `purchase_stock` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_purchase_order_line_qty_stock_available/` |

## Descripción funcional

Muestra el **stock actual** del producto directamente en cada línea del pedido de compra, dentro del formulario del pedido. Así el comprador ve de un vistazo la cantidad disponible en inventario mientras decide la cantidad a pedir, sin necesidad de abrir la ficha del producto.

## Campo(s) añadido(s) o lógica

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `purchase.order.line` | `qty_available` | `Float` | `Stock actual` | Campo `related` hacia `product_id.qty_available`; `readonly=True`. No se almacena (calculado en vivo al leer). |

No se sobrescriben métodos: el campo es puramente relacional.

## Dependencias

| Módulo | Propósito |
|---|---|
| `purchase_stock` (Odoo core) | Provee el campo `qty_available` en `product.product` y la vista base `purchase.purchase_order_form`. |

Sin módulos externos (OCA/terceros).

## Vistas modificadas

| Vista heredada | XPath | Cambio |
|---|---|---|
| `purchase.purchase_order_form` (`purchase.order.form`) | `//field[@name='order_line']/list//field[@name='qty_invoiced']` `position="after"` | Añade la columna `qty_available` con `string="Stock actual"` y `optional="show"` (visible por defecto) en la lista embebida de líneas del pedido de compra. |

## Estructura de archivos

```
klo_purchase_order_line_qty_stock_available/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── purchase.py          ← _inherit de purchase.order.line
├── views/
│   └── purchase_view.xml    ← Hereda purchase_order_form
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_purchase_order_line_qty_stock_available --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_purchase_order_line_qty_stock_available --stop-after-init
```

## Posibles adaptaciones futuras

- Convertir `qty_available` en campo almacenado (`store=True`) si se necesita filtrar/agrupar líneas por stock en listados o informes.
- Añadir también la cantidad entrante prevista (`incoming_qty`) o el stock forecast para dar más contexto al comprador.
- Mostrar el campo en la vista árbol independiente de líneas de pedido de compra, no solo en la lista embebida del formulario.
