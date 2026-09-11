# KLO — Invoice Report Grouped by Sale Order

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_invoice_report_grouped_by_sale_order` |
| Nombre legible   | KLO - Invoice Report Grouped by Sale Order |
| Versión          | `18.0.1.0.1`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | Accounting & Finance                       |
| Dependencias     | `account`, `sale`                          |
| Ubicación        | `extra-addons/klo/extra/klo_invoice_report_grouped_by_sale_order` |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

Este módulo permite imprimir facturas con las líneas agrupadas por pedido de venta, similar a como el módulo OCA `account_invoice_report_grouped_by_picking` agrupa por albarán. El módulo está diseñado para entornos donde no se controla stock y se necesita visualizar el origen de cada línea de factura agrupada por pedido de venta, con subtotales por cada grupo.

---

## Estructura de archivos

```
klo_invoice_report_grouped_by_sale_order/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_move.py
├── views/
│   └── report_invoice.xml
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Modelos afectados

### `account.move`

**Archivo:** `models/account_move.py`  
**Tipo de herencia:** `_inherit`

#### Métodos añadidos

```python
def _sort_grouped_lines(self, lines_dic):
    """
    Ordena las líneas agrupadas por fecha de entrega (commitment_date)
    del pedido de venta, de más reciente a más antigua. Los pedidos sin
    fecha de entrega se ordenan alfabéticamente por nombre al final,
    seguidos de las notas/secciones finales.
    """

def _process_section_note_lines_grouped(
    self, previous_section, previous_note, lines_dic, sale_order=None
):
    """
    Procesa líneas de sección y notas, agrupándolas por pedido.
    """

def _get_grouped_by_sale_order_sorted_lines(self):
    """
    Devuelve las líneas de factura ordenadas para agrupación.
    """

def lines_grouped_by_sale_order(self):
    """
    Prepara la estructura de datos para imprimir el reporte de factura
    agrupado por pedidos de venta. Devuelve una lista de diccionarios con:
    - sale_order: objeto sale.order o vacío
    - line: línea de factura
    - quantity: cantidad para ese grupo
    """
```

---

## Vistas / Templates QWeb modificados

### `account.report_invoice_document`

**Archivo:** `views/report_invoice.xml`  
**ID template:** `klo_invoice_report_grouped_by_sale_order.report_invoice_document`  
**Hereda:** `account.report_invoice_document`

#### Cambios principales

1. Sustituye la iteración sobre `lines` por `lines_grouped` (resultado de `lines_grouped_by_sale_order()`)
2. Añade cabecera de grupo con nombre del pedido de venta y referencia del cliente
3. Muestra subtotales por cada grupo de pedido
4. Ajusta las cantidades mostradas según la agrupación

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Factura con un solo pedido de venta | Se muestra una cabecera con el nombre del pedido y todas sus líneas |
| Factura con varios pedidos de venta | Se muestran cabeceras separadas para cada pedido, con subtotales por cada uno |
| Líneas sin pedido de venta asociado | Se agrupan bajo "Sin referencia" |
| Notas y secciones | Se mantienen dentro del grupo al que pertenecen |
| Notas de crédito | Se muestran con signo negativo correcto |

---

## Instalación y actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_invoice_report_grouped_by_sale_order \
    --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-08-07 | Versión inicial |
| 18.0.1.0.1 | 2026-09-11 | Ordena las agrupaciones por fecha de entrega (commitment_date) de más reciente a más antigua |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)
