# KLO — Ocultar código de producto en informes de pedido y factura

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_sale_invoice_report_hide_product_code` |
| Nombre legible   | KLO - Sale/Invoice report hide product code |
| Versión          | `18.0.1.0.0`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | `Sales/Sales`                              |
| Dependencias     | `sale`, `account`                          |
| Ubicación        | `extra-addons/klo/extra/klo_sale_invoice_report_hide_product_code` |
| Fecha creación   | 2026-09-22                                 |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

El módulo hace que el QWeb de **presupuesto/pedido de venta**
(`sale.report_saleorder_document`) y el de **factura**
(`account.report_invoice_document`) impriman las líneas **sin la referencia
entre corchetes** que suele preceder a la descripción del producto.

Ejemplo de transformación en la impresión:

```
[015622] M. INOXPRES...   →   M. INOXPRES...
```

Solo afecta a la **salida impresa/PDF/HTML** de los informes; el campo `name`
de las líneas se mantiene intacto en base de datos. Funciona tanto para
facturas de venta como para facturas rectificativas (ambas usan
`account.move.line`).

---

## Estructura de archivos

```
klo_sale_invoice_report_hide_product_code/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sale_order_line.py          # Método _get_report_line_name en sale.order.line
│   └── account_move_line.py        # Método _get_report_line_name en account.move.line
├── reports/
│   ├── report_saleorder_document.xml   # Hereda sale.report_saleorder_document
│   └── report_invoice_document.xml     # Hereda account.report_invoice_document
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

---

## Modelos afectados

### `sale.order.line` — Línea de pedido de venta

**Archivo:** `models/sale_order_line.py`
**Tipo de herencia:** `_inherit`

#### Métodos añadidos

```python
def _get_report_line_name(self):
    self.ensure_one()
    if not self.name:
        return ""
    parts = self.name.split("\n", 1)
    first = re.sub(r'^\s*\[[^\]]*\]\s*', '', parts[0])
    if len(parts) > 1:
        return first + "\n" + parts[1]
    return first
```

Devuelve `self.name` sin el prefijo `[CODIGO] ` de la primera línea. No añade
campos.

### `account.move.line` — Línea de factura

**Archivo:** `models/account_move_line.py`
**Tipo de herencia:** `_inherit`

Mismo método `_get_report_line_name()` con idéntica lógica. Cubre facturas de
venta y rectificativas.

---

## Vistas / Templates QWeb modificados

### `sale.report_saleorder_document` — Informe de presupuesto/pedido

**Archivo:** `reports/report_saleorder_document.xml`
**ID template:** `klo_sale_invoice_report_hide_product_code_saleorder`
**Hereda:** `sale.report_saleorder_document`

#### XPath aplicado

```xml
<xpath expr="//td[@name='td_name']" position="replace">
    <td name="td_name"><span t-out="line._get_report_line_name()" t-options="{'widget': 'text'}">Bacon Burger</span></td>
</xpath>
```

**Motivo del cambio:** el `td` original usa `t-field="line.name"`, que imprime
la descripción completa con el código entre corchetes. Se sustituye por
`t-out="line._get_report_line_name()"` que devuelve la descripción limpia.
Se mantiene `name="td_name"` para compatibilidad con otras herencias.

### `account.report_invoice_document` — Informe de factura

**Archivo:** `reports/report_invoice_document.xml`
**ID template:** `klo_sale_invoice_report_hide_product_code_invoice`
**Hereda:** `account.report_invoice_document`

#### XPath aplicado

```xml
<xpath expr="//td[@name='account_invoice_line_name']" position="replace">
    <td name="account_invoice_line_name"><span t-if="line.name" t-out="line._get_report_line_name()" t-options="{'widget': 'text'}" dir="auto">Bacon Burger</span></td>
</xpath>
```

**Motivo del cambio:** idéntico al anterior; se conserva el `t-if="line.name"`
y el atributo `dir="auto"` del original.

---

## Datos de configuración (si aplica)

No carga datos iniciales, ni vistas de formulario, ni reglas de seguridad.

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Línea con `name = "[015622] M. INOXPRES..."` | Se imprime `M. INOXPRES...` |
| Línea con `name` multínea: `"[015622] M. INOXPRES...\nNota extra"` | Se imprime `M. INOXPRES...\nNota extra` (solo se limpia la primera línea) |
| Línea con `name = False` o vacío | Se imprime cadena vacía (`""`) |
| Línea sin corchetes: `"Bacon Burger"` | Se imprime tal cual, sin cambios |
| Factura rectificativa | Se aplica la misma limpieza (usa `account.move.line`) |
| Base de datos | El campo `name` almacenado no se modifica nunca |

---

## Dependencias técnicas internas

- Ninguna. No depende de otros módulos `klo_*`.

---

## Notas para IA / desarrollador

- **Método clave:** `_get_report_line_name()` en `sale.order.line` y
  `account.move.line` — devuelve la descripción sin el prefijo `[CODIGO] `.
- **Regex clave:** `r'^\s*\[[^\]]*\]\s*'` — elimina el corchete inicial (y su
  contenido) más los espacios que lo rodean, solo en la primera línea.
- **Template clave:** `sale.report_saleorder_document` (td `td_name`) y
  `account.report_invoice_document` (td `account_invoice_line_name`).
- **Consideraciones:**
  - El método usa `ensure_one()`; en los informes se llama por línea, así que
    es seguro.
  - `t-out` con `t-options="{'widget': 'text'}"` conserva los saltos de línea
    en la salida HTML/PDF (mismo comportamiento que el `t-field` original).
  - Si en el futuro se quiere ocultar también el código en otros informes
    (albaranes, etc.), basta con reutilizar el mismo método en el QWeb
    correspondiente.
  - La limpieza es solo de presentación: no altera el almacenamiento ni la
    lógica de negocio.

---

## Instalación y actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <db_name> -i klo_sale_invoice_report_hide_product_code --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <db_name> -u klo_sale_invoice_report_hide_product_code --stop-after-init
```

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-09-22 | Versión inicial        |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)