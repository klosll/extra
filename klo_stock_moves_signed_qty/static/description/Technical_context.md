# KLO — Historial de movimientos con cantidad con signo

> Documento técnico generado para uso por IAs en futuros ajustes y adaptaciones.

---

## Identificación del módulo

| Campo          | Valor                                                                   |
|----------------|-------------------------------------------------------------------------|
| Nombre técnico | `klo_stock_moves_signed_qty`                                            |
| Nombre legible | Historial de movimientos con cantidad con signo                         |
| Versión        | `18.0.1.0.0`                                                            |
| Autor          | KLO Ingeniería Informática S.L.L.                                       |
| Licencia       | LGPL-3                                                                  |
| Categoría      | `Inventory`                                                             |
| Dependencias   | `stock`                                                                 |
| Ubicación      | `extra-addons/klo/extra/klo_stock_moves_signed_qty`                     |
| Odoo versión   | 18.0 Community                                                          |

---

## Descripción funcional

Este módulo amplía el **historial de movimientos de stock** de Odoo
(`Inventario → Informes → Historial de movimientos`, modelo `stock.move.line`)
con una columna calculada que indica la **cantidad neta con signo** de cada línea:

- **Positiva (+)** cuando el producto *entra* a una ubicación interna (almacén).
- **Negativa (-)** cuando el producto *sale* de una ubicación interna.
- **Cero (0)** en traslados puramente internos (entre dos ubicaciones internas)
  o puramente externos (ninguna de las dos ubicaciones es interna).

El campo se calcula en el servidor, se almacena en base de datos y se muestra en la
vista lista del historial con:

- Totalización al pie de columna (`sum="Saldo neto"`).
- Formato visual por color: verde para entradas, rojo para salidas, gris para cero.
- Columna opcional (visible por defecto, el usuario puede ocultarla).

> **Nota de diseño:** El docstring de la clase menciona un campo `running_bal`
> (saldo acumulado línea a línea). Este campo **no está implementado** en la versión
> actual (18.0.1.0.0); solo existe `signed_qty`. Si se desea añadir el saldo acumulado
> en el futuro, ver la sección [Posibles adaptaciones futuras](#posibles-adaptaciones-futuras).

---

## Estructura de archivos

```
klo_stock_moves_signed_qty/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── stock_move_line.py          # Herencia de stock.move.line; campo signed_qty
├── views/
│   └── stock_move_line_views.xml   # Herencia de vista lista; columna Cantidad neta
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Modelos afectados

### `stock.move.line` — Líneas de movimiento de stock

**Archivo:** `models/stock_move_line.py`  
**Tipo de herencia:** `_inherit`

#### Campos añadidos

| Campo        | Tipo    | String         | Store | Descripción |
|--------------|---------|----------------|-------|-------------|
| `signed_qty` | `Float` | `Cantidad neta` | `True` | Cantidad con signo: positiva si el destino es interno y el origen no lo es (entrada), negativa si el origen es interno y el destino no lo es (salida), 0 en cualquier otro caso. Usa `qty_done` si el estado es `done`, y `reserved_qty` en caso contrario. |

#### Métodos añadidos

```python
@api.depends('quantity', 'location_id', 'location_dest_id', 'state')
def _compute_signed_qty(self):
    """
    Lógica de signo basada en el tipo de ubicación (usage):
      - dst == 'internal' y src != 'internal'  →  entrada (+qty)
      - src == 'internal' y dst != 'internal'  →  salida  (-qty)
      - ambos iguales (ambos internos o ninguno) →  0
    Cantidad base:
      - En Odoo 18, qty_done y reserved_qty se unifican en el campo `quantity`.
        Se usa `quantity` directamente para todos los estados.
    """
```

**Dependencias del compute:**  
`quantity`, `location_id` (usage), `location_dest_id` (usage), `state`

> **Nota de migración Odoo 18:** Los campos `qty_done` y `reserved_qty` de `stock.move.line`
> fueron eliminados en Odoo 18 y reemplazados por un único campo `quantity`. El campo `state`
> sigue disponible como campo relacionado de `move_id.state`.

**Campos de ubicación relevantes en Odoo:**  
`location_id.usage` y `location_dest_id.usage`. El valor `'internal'` identifica
ubicaciones de almacén propio. Otros valores comunes: `'supplier'`, `'customer'`,
`'transit'`, `'inventory'`, `'production'`.

---

## Vistas modificadas

### `stock.stock_move_line_view_tree` → `stock.view_move_line_tree` — Lista del historial de movimientos

**Archivo:** `views/stock_move_line_views.xml`  
**ID del registro:** `stock_move_line_signed_qty_tree`  
**Modelo:** `stock.move.line`  
**Hereda:** `stock.view_move_line_tree` (módulo `stock`, Odoo core)

> **Nota de migración Odoo 18:** El ID externo de la vista lista cambió de
> `stock.stock_move_line_view_tree` (Odoo ≤17) a `stock.view_move_line_tree` (Odoo 18).

#### XPath aplicado

```xml
<xpath expr="//field[@name='quantity']" position="after">
    <field
        name="signed_qty"
        string="Cantidad neta"
        sum="Saldo neto"
        optional="show"
        decoration-success="signed_qty &gt; 0"
        decoration-danger="signed_qty &lt; 0"
        decoration-muted="signed_qty == 0"
    />
</xpath>
```

**Motivo del cambio:** Se inserta la columna `signed_qty` justo a la derecha de la
columna estándar `quantity` (Cantidad). El atributo `sum` genera automáticamente el
total al pie de la lista. Las decoraciones colorean las filas según el signo
(verde = entrada, rojo = salida, gris = sin movimiento neto).

> **Nota de migración Odoo 18:** El campo de la vista base pasó de llamarse `qty_done`
> a `quantity`, por lo que el XPath apunta a `//field[@name='quantity']`.

---

## Datos de configuración

No se cargan datos de configuración. El módulo no incluye carpeta `data/`, `security/`
ni `demo/`.

---

## Comportamiento esperado

| Situación | Campo `signed_qty` |
|-----------|-------------------|
| Recepción de proveedor (origen: supplier → destino: internal) | `+qty_done` |
| Entrega a cliente (origen: internal → destino: customer) | `-qty_done` |
| Traslado interno (origen: internal → destino: internal) | `0` |
| Movimiento externo puro (origen: supplier → destino: customer) | `0` |
| Movimiento en estado `done` | Usa `qty_done` |
| Movimiento en estado distinto de `done` (ej: `assigned`) | Usa `reserved_qty` |
| Columna en la vista lista | Visible por defecto, ocultable, con total al pie |
| Fila con valor positivo | Color verde (`decoration-success`) |
| Fila con valor negativo | Color rojo (`decoration-danger`) |
| Fila con valor cero | Color gris (`decoration-muted`) |

---

## Dependencias técnicas internas

No hay dependencias de otros módulos `klo_*`. El módulo solo depende del core `stock`.

---

## Notas para IA / desarrollador

- **Campo clave:** `stock.move.line.signed_qty` — Float computado y almacenado.
  El signo se determina exclusivamente por `location_id.usage` y
  `location_dest_id.usage` comparados con el valor `'internal'`.

- **Cantidad base (Odoo 18):** El campo unificado `quantity` reemplaza a los antiguos
  `qty_done` y `reserved_qty`. En Odoo 18 se usa `quantity` directamente sin distinción
  por estado. El campo `state` sigue siendo accesible como campo relacionado de `move_id.state`.

- **Vista heredada:** `stock.view_move_line_tree` es el ID externo de la vista lista
  estándar del historial de movimientos en Odoo 18. En versiones anteriores (≤17) se
  llamaba `stock.stock_move_line_view_tree`. Si Odoo la renombra en versiones futuras,
  el `inherit_id` puede fallar. Verificar con `ir.ui.view` en la BD.

- **`store=True`:** El campo se almacena en la columna `signed_qty` de la tabla
  `stock_move_line`. Esto permite filtrarlo, ordenarlo y agregarlo en informes SQL.
  Si se cambia la lógica de cálculo, hay que recomputar el campo en toda la tabla.

- **Campo `running_bal` no implementado:** El docstring de la clase menciona un
  campo `running_bal` (saldo acumulado). No existe en el código. Si se necesita,
  debe implementarse como campo no almacenado (`store=False`) con compute que
  requiera ordenar todas las líneas del mismo producto por fecha — o bien calcularse
  en un wizard/informe separado, ya que la computación en lote puede ser costosa.

- **Limitación de `quantity` en Odoo 18:** El campo unificado `quantity` puede
  representar tanto cantidad reservada (movimientos pendientes) como cantidad
  realizada (movimientos `done`). En Odoo ≤17 existían `qty_done` y `reserved_qty`
  por separado. Considerar el contexto del movimiento si se extiende la lógica.

---

## Posibles adaptaciones futuras

1. **Añadir saldo acumulado (`running_bal`):**  
   Implementar un campo `Float` computado (sin `store`) que, para un conjunto de
   líneas filtradas por producto y ordenadas por fecha, calcule la suma acumulada
   de `signed_qty`. Requeriría búsqueda de todas las líneas anteriores del mismo
   producto, lo que puede ser costoso; valorar ejecutarlo solo en un wizard o
   informe específico.

2. **Filtrar por almacén en lugar de por ubicación interna:**  
   Actualmente el signo se basa en `usage == 'internal'`. Si se necesita calcular
   entradas/salidas respecto a un almacén concreto (no a todas las ubicaciones
   internas), habría que comparar `location_id` y `location_dest_id` contra el
   conjunto de ubicaciones del almacén seleccionado.

3. **Exportar el campo en informes XLSX/PDF:**  
   El campo está almacenado, por lo que puede incluirse fácilmente en cualquier
   informe QWeb o de BI añadiéndolo al dominio/campo del informe.

4. **Extender a `stock.move` (cabecera):**  
   Si se desea la misma lógica a nivel de movimiento (no de línea), se puede
   heredar `stock.move` con el mismo patrón, usando `move_line_ids.signed_qty`
   como dependencia.

---

## Instalación y actualización

```bash
# Instalar por primera vez
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -i klo_stock_moves_signed_qty \
    --stop-after-init

# Actualizar tras cambios
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_stock_moves_signed_qty \
    --stop-after-init
```

> Bases de datos activas habituales: `ryp_dev`, `myv_dev`, `proyecta79_dev`,
> `victorperez_dev`, `viliman_dev`.

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio                                 |
|------------|------------|--------------------------------------------------------|
| 18.0.1.0.0 | —          | Versión inicial: campo `signed_qty` + vista lista      |
| 18.0.1.0.0 | 2026-06-25 | Corrección Odoo 18: `qty_done`/`reserved_qty` → `quantity`; vista heredada `stock.view_move_line_tree` |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)
