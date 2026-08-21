# KLO — Sale Order Line Menu with Product Category and Order Date

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_sale_order_line_menu_product_category` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | Open Source Integrators, OCA, KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales/Sales |
| **Dependencias** | `sale`, `sale_order_line_menu` (OCA) |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_sale_order_line_menu_product_category/` |

---

## Descripción funcional

Amplía el módulo OCA `sale_order_line_menu` para que en la lista global de líneas de pedido de venta se pueda visualizar y agrupar por **Categoría de producto** y por **Fecha del pedido**. Esto permite filtrar y agrupar líneas de distintos pedidos bajo un mismo criterio analítico.

---

## Campo(s) añadido(s)

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `sale.order.line` | `date_order` | Datetime | (sin string explícito, usa etiqueta del campo relacionado) | `related="order_id.date_order"`, `readonly=True`, `store=True`, `index=True`. Permite agrupar/buscar por fecha de pedido en la línea. |
| `sale.order.line` | `product_categ_id` | Many2one (`product.category`) | Product Category | `related="product_id.categ_id"`, `readonly=True`. No se almacena. |

No se sobrescriben métodos.

> **Nota:** El campo `date_order` se añade al modelo con `store=True` e `index=True` para permitir agrupamiento y búsqueda eficiente, pero **no se muestra explícitamente en la vista árbol** del módulo. La vista solo expone `product_categ_id`. El campo `date_order` queda disponible para filtros, agrupamientos y vistas personalizadas.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` | Modelo base `sale.order.line` y `sale.order` |
| `sale_order_line_menu` (OCA) | Provee el menú y la vista árbol `sale_order_line_tree` que se hereda |

El módulo OCA reside en:
`/opt/odoo18_desarrollo/extra-addons/oca/sale-workflow/sale_order_line_menu/`

---

## Vistas modificadas

### Vista árbol de líneas de pedido de venta

| Atributo | Valor |
|---|---|
| **Vista heredada** | `sale_order_line_menu.sale_order_line_tree` |
| **Modo** | `extension` |
| **XPath** | `//field[@name='name']` posición `after` |
| **Cambio** | Añade `<field name="product_categ_id" optional="show" />` |

La columna de categoría aparece visible por defecto gracias a `optional="show"`.

---

## Estructura de archivos

```
klo_sale_order_line_menu_product_category/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line.py     ← Añade date_order (store) y product_categ_id (related)
├── views/
│   └── sale_order_line_views.xml   ← Hereda vista árbol OCA
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_sale_order_line_menu_product_category --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_sale_order_line_menu_product_category --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Añadir la columna `date_order` a la vista árbol para que sea visible además de filtrable.
- Incluir filtros de búsqueda por categoría de producto en la vista árbol.
- Considerar `store=True` en `product_categ_id` si se necesitan informes o consultas SQL que filtren por categoría sin recorrer la relación en tiempo real.
