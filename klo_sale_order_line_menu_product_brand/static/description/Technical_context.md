# KLO — Sale Order Line Menu with Product Brand

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_sale_order_line_menu_product_brand` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | Open Source Integrators, OCA, KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales/Sales |
| **Dependencias** | `sale`, `sale_order_line_menu` (OCA) |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_sale_order_line_menu_product_brand/` |

---

## Descripción funcional

Amplía el módulo OCA `sale_order_line_menu` —que añade un menú de líneas de pedido de venta a nivel global— para que en dicha lista se pueda visualizar y agrupar por **Marca de producto**. Sin este módulo, la vista de líneas de pedido de venta no expone la marca del producto asociado a cada línea.

---

## Campo(s) añadido(s)

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `sale.order.line` | `product_brand_id` | Many2one (`product.brand`) | Product Brand | Campo relacionado (`related`) con `product_id.product_brand_id`; `readonly=True`. No se almacena (related sin store). |

No se sobrescriben métodos.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` | Modelo base `sale.order.line` |
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
| **Cambio** | Añade `<field name="product_brand_id" optional="show" />` |

La columna aparece visible por defecto gracias a `optional="show"`.

---

## Estructura de archivos

```
klo_sale_order_line_menu_product_brand/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order_line.py     ← Añade product_brand_id (related)
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
  -d myv_dev -i klo_sale_order_line_menu_product_brand --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_sale_order_line_menu_product_brand --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Añadir la marca también en la vista formulario de línea de pedido de venta si se necesita edición o consulta detallada.
- Incluir filtros de búsqueda por marca en la vista árbol para facilitar el agrupamiento.
- Considerar `store=True` en `product_brand_id` si se necesitan consultas SQL o informes que filtren por marca sin recorrer la relación en tiempo real.
