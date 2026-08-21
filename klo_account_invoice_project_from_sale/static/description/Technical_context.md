# KLO — Project on Invoice from Origin Sale Order

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_account_invoice_project_from_sale` |
| **Versión** | 18.0.1.0.1 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting |
| **Dependencias** | `account`, `sale`, `sale_project`, `project` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_account_invoice_project_from_sale/` |

---

## Descripción funcional

Vincula automáticamente el **proyecto** asociado a un pedido de venta con la factura generada a partir de dicho pedido. Cuando se factura un pedido de venta que tiene un proyecto asignado (vía `sale_project`), la factura hereda el proyecto sin necesidad de selección manual. Además, imprime el proyecto tanto en el informe de pedido de venta como en el informe de factura.

---

## Campo(s) añadido(s)

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `account.move` | `sale_order_id` | Many2one (`sale.order`) | Sales Order | `compute="_compute_sale_order_id"`, `store=True`, `index=True`, `copy=False`. Almacena el pedido de venta origen de la factura. |
| `account.move` | `project_id` | Many2one (`project.project`) | Project | `related="sale_order_id.project_id"`, `store=True`, `copy=False`, `readonly=False` (editable). Hereda el proyecto del pedido de venta origen. |

### Método sobrescrito: `_compute_sale_order_id`

```python
@api.depends('invoice_line_ids.sale_line_ids')
def _compute_sale_order_id(self):
    for move in self:
        sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
        move.sale_order_id = sale_orders[0] if sale_orders else False
```

- **Dependencias:** `invoice_line_ids.sale_line_ids` — se recalcula cuando cambian las líneas de venta vinculadas a las líneas de factura.
- **Lógica:** toma el primer pedido de venta encontrado entre todas las líneas de factura. Si no hay líneas de venta vinculadas, deja `sale_order_id` en `False`.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` | Modelo base `account.move` y vista formulario `account.view_move_form` |
| `sale` | Modelo `sale.order` y plantilla `sale.report_saleorder_document` |
| `sale_project` | Vincula pedidos de venta con proyectos (`sale.order.project_id`) |
| `project` | Modelo `project.project` |

No depende de módulos externos fuera del núcleo.

---

## Vistas / Plantillas modificadas

### Formulario de factura

| Atributo | Valor |
|---|---|
| **Vista heredada** | `account.view_move_form` |
| **XPath** | `//group[@name='sale_info_group']/*[1]` posición `before` |
| **Cambio** | Añade `<field name="project_id" invisible="move_type not in ('out_invoice', 'out_refund')" />` |

El campo proyecto solo es visible en facturas y abonos de cliente.

### Informe de pedido de venta

| Atributo | Valor |
|---|---|
| **Plantilla heredada** | `sale.report_saleorder_document` |
| **XPath** | `//div[@id='informations']` posición `inside` |
| **Cambio** | Añade un `div` con etiqueta "Proyecto" y `t-field="doc.project_id"`, visible si `doc.project_id` existe |

### Informe de factura

| Atributo | Valor |
|---|---|
| **Plantilla heredada** | `account.report_invoice_document` |
| **XPath** | `//div[@name='origin']` posición `after` |
| **Cambio** | Añade un `div` con etiqueta "Project" y `t-field="o.project_id"`, visible si `o.project_id` existe |

---

## Estructura de archivos

```
klo_account_invoice_project_from_sale/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_move.py          ← Añade sale_order_id (compute) y project_id (related)
├── views/
│   └── account_move_view.xml    ← Añade project_id al formulario de factura
├── reports/
│   ├── sale_order_templates.xml ← Imprime proyecto en informe de pedido
│   └── invoice_report.xml       ← Imprime proyecto en informe de factura
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_account_invoice_project_from_sale --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_account_invoice_project_from_sale --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Gestionar facturas con líneas de varios pedidos: actualmente se toma solo el primer pedido (`sale_orders[0]`). Si se necesita soporte multi-pedido, se podría usar un campo `Many2many` o mostrar un campo calculado de texto.
- Hacer `project_id` solo lectura si se desea impedir la edición manual en la factura.
- Añadir el proyecto como columna en la vista árbol de facturas para filtrado rápido.
