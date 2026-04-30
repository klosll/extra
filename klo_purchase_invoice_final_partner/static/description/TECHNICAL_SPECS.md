# KLO Purchase and Invoice Final Partner - Especificaciones Técnicas

## Informacion General

| Campo | Valor |
|-------|-------|
| **Nombre del Modulo** | `klo_purchase_invoice_final_partner` |
| **Nombre Tecnico** | KLO Purchase and Invoice Final Partner |
| **Version** | 15.0.1.5.7 |
| **Categoria** | Purchase |
| **Licencia** | AGPL-3 |
| **Autor** | KLO Ingenieria Informatica S.L.L. |
| **Website** | https://www.klo.es |
| **Version de Odoo** | 15.0 |

## Objetivo del Modulo

Este modulo extiende la funcionalidad de compras y facturacion de Odoo 15 para permitir la asignacion de un **"Cliente de venta"** (`sale_partner_id`) en:

- Pedidos de compra (cabecera y lineas)
- Facturas de compra (cabecera y lineas)
- Lineas analiticas generadas desde facturas: el cliente de venta se asigna al campo estandar `partner_id` de `account.analytic.line`

El objetivo principal es poder rastrear **para que cliente final** se realizo una compra o gasto, facilitando la imputacion analitica y el seguimiento de costes por cliente.

---

## Funcionalidades Principales

### 1. Cliente de Venta en Pedidos de Compra

#### Cabecera del Pedido (`purchase.order`)
- Aniade el campo `sale_partner_id` (Many2one a `res.partner`)
- Permite indicar el cliente final para el que se realiza la compra
- Visible en la vista formulario despues del campo "Referencia del proveedor"
- Opcional en la vista arbol (columna oculta por defecto)

#### Lineas del Pedido (`purchase.order.line`)
- Aniade el campo `sale_partner_id` en cada linea
- Se auto-completa desde la cabecera del pedido mediante `@api.depends`
- Es **editable** por linea, permitiendo diferentes clientes por producto
- Visible en el arbol de lineas despues de "Cuenta analitica"

**Comportamiento**:
```python
@api.depends('order_id.sale_partner_id')
def _compute_sale_partner_id(self):
    # Solo asigna si la linea aun no tiene valor propio guardado
    if not line._origin.sale_partner_id:
        line.sale_partner_id = line.order_id.sale_partner_id
```

---

### 2. Cliente de Venta en Facturas de Compra

#### Cabecera de la Factura (`account.move`)
- Aniade el campo `sale_partner_id` (Many2one a `res.partner`)
- Se hereda automaticamente desde el pedido de compra al facturar mediante `_prepare_invoice()`
- Visible en la vista formulario despues del campo "Referencia"

#### Lineas de la Factura (`account.move.line`)
- Aniade el campo `sale_partner_id` en cada linea
- **Prioridad de asignacion automatica en `create()`**:
  1. Si proviene de un pedido de compra: usa `purchase_line_id.sale_partner_id`
  2. Si no: usa `move_id.sale_partner_id` de la cabecera
- Solo se asigna automaticamente si `sale_partner_id` **no viene incluido** en `vals`
- Es **editable** manualmente en cualquier momento
- Visible en el arbol de lineas de factura despues de `analytic_account_id`

> **Arquitectura actual (v15.0.1.5.7)**: El campo es completamente **simple** (sin compute,
> sin onchange). La proteccion y propagacion se implementa en tres capas:
>
> | Capa | Mecanismo | Cuando actua |
> |------|-----------|--------------|
> | **UI - pre-fill** | Vista `klo_view_move_invoice_line_context` + `default_get()` | Al añadir nueva linea en el formulario |
> | **Creacion** | `AccountMoveLine.create()` | Al crear lineas programaticamente (facturacion de pedido, etc.) |
> | **Guardado** | `AccountMove.write()` | Al guardar el formulario (proteccion contra autocompletado de Odoo) |

---

### 3. Propagacion a Lineas Analiticas

> **Cambio en v15.0.1.5.0**: El campo `sale_partner_id` se elimino de `account.analytic.line`.
> El "Cliente de venta" de `account.move.line` se propaga ahora al campo estandar `partner_id`
> de `account.analytic.line` al validar la factura de compra.

Al confirmar la factura (`action_post`) se producen tres acciones sobre las lineas analiticas:

**A) Lineas creadas por `analytic_account_id` (via `_prepare_analytic_line`)**

El `sale_partner_id` de la linea de factura se asigna como `partner_id` del apunte analitico:
```python
def _prepare_analytic_line(self):
    result = super()._prepare_analytic_line()
    for i, move_line in enumerate(self):
        if move_line.sale_partner_id and i < len(result):
            result[i]['partner_id'] = move_line.sale_partner_id.id
    return result
```

**B) Lineas creadas por distribucion de etiquetas (via `_prepare_analytic_distribution_line`)**
```python
def _prepare_analytic_distribution_line(self, distribution):
    result = super()._prepare_analytic_distribution_line(distribution)
    if self.sale_partner_id:
        result['partner_id'] = self.sale_partner_id.id
    return result
```

**C) Lineas creadas por templates analiticos del modulo AvanzOSC (`analytic_template_ids`)**

El modulo `account_analytic_distribution` (AvanzOSC) crea lineas analiticas adicionales en
su propio `action_post()` basandose en `account_id.analytic_template_ids`. Estas lineas quedan
vinculadas a la factura mediante `analytic_line_ids` (campo `account_move_id`).

Nuestro `action_post()` las gestiona despues del `super()`:
1. **Elimina** las que tengan `amount=0.0` y `move_id.balance != 0.0`
2. **Propaga** `sale_partner_id` → `partner_id` en las que quedan validas

```python
def action_post(self):
    result = super().action_post()
    for move in self:
        lines_to_delete = move.analytic_line_ids.filtered(
            lambda al: al.amount == 0.0 and al.move_id and al.move_id.balance != 0.0
        )
        if lines_to_delete:
            lines_to_delete.unlink()
        for analytic_line in move.analytic_line_ids:
            invoice_line = analytic_line.move_id
            if invoice_line and invoice_line.sale_partner_id and not analytic_line.partner_id:
                analytic_line.partner_id = invoice_line.sale_partner_id
    return result
```

---

## Flujo de Datos

```
+-------------------------+
|  Pedido de Compra       |
|  purchase.order         |
|  +-------------------+  |
|  | sale_partner_id   |--+--+
|  +-------------------+  |  |
|          |              |  |
|          v              |  |
|  +-------------------+  |  |
|  | Lineas del Pedido |  |  |
|  | sale_partner_id   |  |  |
|  +-------------------+  |  |
+-------------------------+  |
          |                  |
          | Facturar         | _prepare_invoice()
          v                  |
+-------------------------+  |
|  Factura de Compra      |  |
|  account.move           |  |
|  +-------------------+  |<-+
|  | sale_partner_id   |  |
|  +-------------------+  |
|          |              |
|          v              |
|  +-------------------+  |
|  | Lineas Factura    |  |
|  | sale_partner_id   |--+--+
|  +-------------------+  |  |
+-------------------------+  |
          |                  | action_post():
          |                  | sale_partner_id -> partner_id
          v                  | (3 mecanismos analytic)
+-------------------------+  |
|  Apuntes Analiticos     |  |
|  account.analytic.line  |  |
|  +-------------------+  |<-+
|  | partner_id        |  |  <- Campo ESTANDAR de Odoo
|  +-------------------+  |
+-------------------------+
```

---

## Arquitectura del Modulo

### Estructura de Archivos

```
klo_purchase_invoice_final_partner/
+-- __init__.py
+-- __manifest__.py
+-- models/
|   +-- __init__.py
|   +-- purchase.py              # PurchaseOrder, PurchaseOrderLine
|   +-- account_move.py          # AccountMove (write, action_post), AccountMoveLine
|   +-- account_analytic_line.py # Solo comentario explicativo (sin campos adicionales)
+-- views/
|   +-- purchase_view.xml        # Vistas de pedidos de compra
|   +-- account_move_view.xml    # Vistas de facturas (3 records de vista)
|   +-- account_analytic_line_view.xml  # Sin vistas activas (comentario explicativo)
+-- static/
    +-- description/
        +-- icon.png
        +-- TECHNICAL_SPECS.md   # Este archivo
```

### Dependencias del Modulo

```python
"depends": [
    "purchase_stock",           # Gestion de compras con inventario
    "account",                  # Modulo de contabilidad
    "analytic",                 # Cuentas analiticas
    "account_analytic_distribution",  # Distribucion analitica por etiquetas (AvanzOSC)
]
```

---

## Modelo de Datos

### Campos Aniadidos

#### `purchase.order`
```python
sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)
```

#### `purchase.order.line`
```python
sale_partner_id = fields.Many2one(
    'res.partner', string='Cliente de venta',
    compute='_compute_sale_partner_id', store=True, readonly=False,
)
```

#### `account.move`
```python
sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta', required=False)
```

#### `account.move.line`
```python
# Campo simple sin compute, sin onchange, sin readonly.
# La propagacion inicial se hace SOLO en create() y via default_get() en la UI.
# Una vez creada la linea, el campo es completamente inerte salvo edicion manual.
sale_partner_id = fields.Many2one('res.partner', string='Cliente de venta')
```

#### `account.analytic.line`
> **v15.0.1.5.0**: NO se aniade ningun campo nuevo. El "Cliente de venta" se propaga
> al campo estandar `partner_id` que ya existe en el modelo.

### Relaciones entre Modelos

```
res.partner <-- Many2one --- purchase.order.sale_partner_id
res.partner <-- Many2one --- purchase.order.line.sale_partner_id
res.partner <-- Many2one --- account.move.sale_partner_id
res.partner <-- Many2one --- account.move.line.sale_partner_id
res.partner <-- Many2one --- account.analytic.line.partner_id  (campo estandar Odoo)
```

---

## Metodos Principales Override

### 1. `purchase.order._prepare_invoice()`

**Proposito**: Propagar `sale_partner_id` de pedido a factura al facturar.

```python
def _prepare_invoice(self):
    invoice_vals = super()._prepare_invoice()
    invoice_vals['sale_partner_id'] = self.sale_partner_id.id
    return invoice_vals
```

---

### 2. `purchase.order.line._prepare_account_move_line()`

**Proposito**: Propagar `sale_partner_id` y pre-computar `analytic_account_id` al crear lineas de factura desde pedido.

```python
def _prepare_account_move_line(self, move=False):
    result = super()._prepare_account_move_line(move=move)
    if self.sale_partner_id:
        result['sale_partner_id'] = self.sale_partner_id.id
    if not result.get('analytic_account_id') and not self.display_type and self.product_id:
        # Buscar cuenta analitica por cuenta de gasto del articulo
        accounts = self.product_id.product_tmpl_id.with_company(company).get_product_accounts(...)
        expense_account = accounts.get('expense') or move.journal_id.default_account_id
        if expense_account:
            rec = self.env['account.analytic.default'].account_get(
                product_id=self.product_id.id, account_id=expense_account.id, ...)
            if rec:
                result['analytic_account_id'] = rec.analytic_id.id
    return result
```

---

### 3. `AccountMove.write()` *(nuevo en v15.0.1.5.6)*

**Proposito**: Proteger `sale_partner_id` en lineas contra sobreescritura por el mecanismo de
autocompletado interno de Odoo (`_move_autocomplete_invoice_lines_write`).

**Problema que resuelve**: Cuando el cliente web guarda una factura y Odoo ejecuta su autocompletado
interno (ej. al cambiar proveedor, divisa, plazo de pago), el mecanismo reconstruye las lineas desde
la BD sin incluir campos "no contables" como `sale_partner_id`. Esto puede sobreescribir los valores
asignados manualmente.

**Mecanismo**:
1. Antes del `write()` captura los `sale_partner_id` **explicitamente enviados** en los `vals` de cada
   linea (`cmd=1` para existentes, `cmd=0` para nuevas)
2. Ejecuta el `super().write()` estandar
3. Tras el write, verifica si los valores se aplicaron; si no, los re-aplica directamente

```python
def write(self, vals):
    explicit_sale_partners = {}   # {line_id: sale_partner_id}  — lineas existentes (cmd=1)
    new_line_sale_partners = []   # [sale_partner_id, ...]       — lineas nuevas (cmd=0)

    for key in ('invoice_line_ids', 'line_ids'):
        for cmd in vals.get(key, []):
            if isinstance(cmd, (list, tuple)) and len(cmd) >= 3:
                cmd_type, line_id, cmd_vals = cmd[0], cmd[1], cmd[2]
                if isinstance(cmd_vals, dict):
                    if cmd_type == 1 and 'sale_partner_id' in cmd_vals:
                        explicit_sale_partners[line_id] = cmd_vals['sale_partner_id']
                    elif cmd_type == 0 and 'sale_partner_id' in cmd_vals:
                        new_line_sale_partners.append(cmd_vals['sale_partner_id'])

    existing_line_ids = set()
    if new_line_sale_partners:
        for move in self:
            existing_line_ids.update(move.line_ids.ids)

    result = super().write(vals)

    # Re-aplicar en lineas EXISTENTES si el autocompletado perdio el valor
    for line_id, spid in explicit_sale_partners.items():
        line = self.env['account.move.line'].browse(line_id)
        if line.exists() and (line.sale_partner_id.id or False) != (spid or False):
            _logger.warning("KLO PROTECCION: ...")
            self.env['account.move.line'].browse(line_id).write({'sale_partner_id': spid or False})

    # Re-aplicar en lineas NUEVAS (emparejadas por orden de creacion)
    if new_line_sale_partners:
        idx = 0
        for move in self:
            new_lines = move.line_ids.filtered(lambda l: l.id not in existing_line_ids)
            for line in new_lines:
                if idx >= len(new_line_sale_partners):
                    break
                expected = new_line_sale_partners[idx] or False
                if (line.sale_partner_id.id or False) != expected:
                    _logger.warning("KLO PROTECCION (nueva linea): ...")
                    line.write({'sale_partner_id': expected})
                idx += 1

    return result
```

> **Nota**: El re-write se hace directamente sobre `account.move.line` para evitar recursion.
> El `_logger.warning` se emite solo cuando se detecta discrepancia, facilitando diagnostico.

---

### 4. `AccountMoveLine.default_get()` *(nuevo en v15.0.1.5.7)*

**Proposito**: Pre-rellenar `sale_partner_id` cuando el usuario añade una nueva linea en el
formulario de factura desde la UI.

**Mecanismo primario**: La vista `klo_view_move_invoice_line_context` inyecta
`default_sale_partner_id: sale_partner_id` en el contexto de `invoice_line_ids`. Odoo base
procesa automaticamente los `default_*` del contexto en `default_get`, por lo que el valor ya
llega en `defaults` antes del codigo KLO.

**Este metodo actua como fallback** para creacion programatica donde se pase `default_move_id`
en contexto pero no `default_sale_partner_id`:

```python
@api.model
def default_get(self, fields_list):
    defaults = super().default_get(fields_list)
    if 'sale_partner_id' not in defaults:
        move_id = self.env.context.get('default_move_id') or self.env.context.get('move_id')
        if move_id:
            move = self.env['account.move'].browse(move_id)
            if move.sale_partner_id:
                defaults['sale_partner_id'] = move.sale_partner_id.id
    return defaults
```

**Interaccion con `create()`**: El valor por defecto (o el modificado por el usuario) llega en
`vals` con clave `sale_partner_id`. Como `create()` usa `'sale_partner_id' not in vals`, respeta
siempre el valor que llega sin sobreescribirlo.

---

### 5. `AccountMoveLine.create()` *(condicion corregida en v15.0.1.5.6)*

**Proposito**: Al crear lineas programaticamente, asignar `sale_partner_id` si no viene ya informado.

**Correccion clave (v15.0.1.5.6)**: `not vals.get('sale_partner_id')` → `'sale_partner_id' not in vals`

| Condicion | `vals={}` | `vals={'sale_partner_id': False}` | `vals={'sale_partner_id': 42}` |
|-----------|-----------|----------------------------------|-------------------------------|
| `not vals.get(...)` | True ✅ asigna | True ❌ sobreescribira borrado | False ✅ respeta |
| `... not in vals`   | True ✅ asigna | False ✅ respeta borrado     | False ✅ respeta |

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if 'sale_partner_id' not in vals:
            # Prioridad 1: linea del pedido de compra
            purchase_line_id = vals.get('purchase_line_id')
            if purchase_line_id:
                purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                if purchase_line.sale_partner_id:
                    vals['sale_partner_id'] = purchase_line.sale_partner_id.id
                    continue
            # Prioridad 2: cabecera de la factura
            move_id = vals.get('move_id')
            if move_id:
                move = self.env['account.move'].browse(move_id)
                if move.sale_partner_id:
                    vals['sale_partner_id'] = move.sale_partner_id.id
    return super().create(vals_list)
```

---

### 6. `account.move.line._compute_analytic_account_id()`

**Proposito**: Override con fallback a cuenta por defecto del diario cuando la logica estandar no encuentra regla analitica.

```python
@api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.journal_id')
def _compute_analytic_account_id(self):
    super()._compute_analytic_account_id()  # Paso 1: logica estandar
    for record in self:
        if not record.analytic_account_id:  # Paso 2: fallback al diario
            journal_default_account = record.move_id.journal_id.default_account_id
            if journal_default_account:
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    account_id=journal_default_account.id, ...)
                if rec:
                    record.analytic_account_id = rec.analytic_id
```

---

### 7. `account.move.line._prepare_analytic_line()` y `_prepare_analytic_distribution_line()`

Propagan `sale_partner_id` → `partner_id` en los dos mecanismos estandar de creacion de lineas analiticas (cuenta analitica directa y distribucion por etiquetas). Ver seccion 3 para el codigo completo.

---

## Comportamiento del Modulo `account_analytic_distribution` (AvanzOSC)

Este modulo crea lineas analiticas adicionales al validar facturas, basandose en
`analytic_template_ids` de la cuenta contable. Las lineas resultantes se identifican por tener
`account_move_id != NULL` en `account.analytic.line`.

> **Recomendacion**: Los templates activos deberian tener `percentage=100` para generar importes
> correctos. Configurar desde `Contabilidad > Configuracion > Plantillas analiticas`.

---

## Interfaces de Usuario

### Vistas Implementadas

#### 1. Pedidos de Compra (`purchase_view.xml`)

- **Vista Arbol**: columna `sale_partner_id` opcional (oculta por defecto) tras `partner_id`
- **Cabecera del formulario**: campo `sale_partner_id` tras `partner_ref`
- **Arbol de lineas**: campo `sale_partner_id` opcional tras `account_analytic_id`

#### 2. Facturas de Compra (`account_move_view.xml`) — tres records

**`klo_view_move_final_partner_form`**:
- Campo `sale_partner_id` en la cabecera del formulario, tras `ref`

**`klo_view_move_line_sale_partner_form`**:
- Columna `sale_partner_id` en el arbol de lineas, tras `analytic_account_id`
- `optional="show"` (visible por defecto)
- **Razon del `optional="show"`**: con `optional="hide"` el cliente web OWL omite el campo del
  payload al guardar/onchange cuando la columna esta oculta, provocando que `write()` no capture
  el valor explicitamente y `create()` lo sobreescriba con el de la cabecera

**`klo_view_move_invoice_line_context`** *(nuevo en v15.0.1.5.7)*:
- Modifica el atributo `context` del campo `invoice_line_ids` para inyectar `default_sale_partner_id`
- Cuando el usuario hace clic en "Añadir una linea", el cliente web incluye `default_sale_partner_id`
  en el contexto de la llamada a `default_get`, y Odoo base lo procesa automaticamente
- La nueva linea aparece pre-rellenada con el `sale_partner_id` de la cabecera
- Si el usuario modifica el valor antes de guardar, `create()` respeta el valor final

```xml
<!-- Replica el contexto base de invoice_line_ids + añade default_sale_partner_id -->
<xpath expr="//field[@name='invoice_line_ids']" position="attributes">
    <attribute name="context">
        {'default_move_type': context.get('default_move_type'),
         'journal_id': journal_id,
         'default_partner_id': commercial_partner_id,
         'default_currency_id': currency_id or company_currency_id,
         'default_sale_partner_id': sale_partner_id}
    </attribute>
</xpath>
```

> **Nota de mantenimiento**: El contexto replica el contexto base de `invoice_line_ids` definido en
> `account/views/account_move_views.xml` (linea ~884). Si Odoo actualiza ese contexto base, revisar
> este xpath para mantener consistencia.

#### 3. Apuntes Analiticos

> **v15.0.1.5.0**: No hay vistas adicionales. El campo `partner_id` estandar ya es visible
> de forma nativa en todas las vistas de `account.analytic.line`.

---

## Casos de Uso

### Caso 1: Compra para Cliente Especifico
1. Crear pedido → asignar "Cliente de venta" en cabecera → las lineas lo heredan
2. Facturar → el cliente se propaga a la cabecera de la factura
3. Al validar: `partner_id` de todos los apuntes analiticos = cliente de venta

### Caso 2: Compra Multi-Cliente
1. Crear pedido → asignar diferentes "Clientes de venta" en cada linea
2. Al facturar, cada linea de factura mantiene su cliente especifico
3. Los apuntes analiticos reflejan el cliente correcto por linea

### Caso 3: Modificacion Manual en Factura Borrador
1. Abrir factura borrador → cambiar `sale_partner_id` en la linea deseada
2. Guardar: el `write()` garantiza que el valor persiste aunque el autocompletado lo omita

### Caso 4: Nueva Linea con Valor por Defecto desde Cabecera
1. Abrir factura borrador con `sale_partner_id` en cabecera
2. Hacer clic en "Añadir una linea" → la linea aparece pre-rellenada con el valor de la cabecera
3. Si se quiere un cliente diferente: cambiar antes de guardar
4. Al guardar, `create()` respeta el valor final (el por defecto o el modificado)

---

## Consideraciones Tecnicas

### Por Que Tres Capas de Proteccion

El autocompletado interno de Odoo (`_move_autocomplete_invoice_lines_write`) puede reconstruir
lineas sin incluir `sale_partner_id`. La solucion requiere tres capas complementarias:

| Capa | Mecanismo | Problema que previene |
|------|-----------|----------------------|
| Vista context + `default_get` | `default_sale_partner_id` en contexto | La linea nueva no se inicializa con el valor de la cabecera |
| `create()` con `'field' not in vals` | Condicion estricta | No heredar valor si la UI no lo envio explicitamente |
| `write()` con re-aplicacion | Captura y verificacion post-write | El autocompletado de Odoo sobreescribe al guardar |

### Distincion `not vals.get(f)` vs `f not in vals`

Esta distincion es critica en `create()`:
```python
vals = {'sale_partner_id': False}  # Usuario borro explicitamente el valor
not vals.get('sale_partner_id')    # True  → sobreescribiria el borrado deliberado ❌
'sale_partner_id' not in vals      # False → respeta el borrado deliberado       ✅

vals = {}                          # Campo no enviado
not vals.get('sale_partner_id')    # True  → asigna valor por defecto ✅
'sale_partner_id' not in vals      # True  → asigna valor por defecto ✅
```

### Propagacion en Cascada

```
Pedido (sale_partner_id) → Factura (sale_partner_id) → Analitica (partner_id)
```

- La propagacion ocurre en la **creacion** de registros
- Modificaciones posteriores NO se propagan automaticamente hacia adelante
- El `write()` solo protege contra perdida involuntaria, no propaga cambios en cascada

### Tres Mecanismos de Creacion de Lineas Analiticas

| Mecanismo | Metodo | Cuando | Partner propagado |
|-----------|--------|--------|------------------|
| Cuenta analitica directa | `_prepare_analytic_line()` | Al validar, si `analytic_account_id` | Si |
| Distribucion por etiquetas | `_prepare_analytic_distribution_line()` | Al validar, si `analytic_distribution` | Si |
| Templates AvanzOSC | `action_post()` de AvanzOSC + nuestro post-proceso | Al validar, si `analytic_template_ids` | Si (post-proceso) |

### Cadena de Prioridad para `analytic_account_id` (v15.0.1.4.0)

```
1. ¿Tiene la linea analytic_account_id manual? → Usar ese valor
      |
      v No
2. ¿Hay regla account.analytic.default para la cuenta contable de gasto del articulo?
      | Si → Asignar
      v No
3. ¿Hay regla account.analytic.default para la cuenta por defecto del diario?
      | Si → Asignar (fallback KLO en _compute_analytic_account_id)
      v No
4. Sin cuenta analitica
```

---

## Testing y Validacion

### Pruebas Recomendadas

1. **Propagacion basica**: pedido → factura → apuntes analiticos
2. **Edicion manual en linea existente**: cambiar valor → guardar → verificar que persiste (no sobreescrito por autocompletado)
3. **Nueva linea con valor por defecto desde cabecera** *(v15.0.1.5.7)*: abrir factura con cabecera rellena → añadir linea → verificar pre-relleno → modificar antes de guardar → verificar que persiste el valor modificado
4. **Nueva linea sin cabecera rellena**: verificar que el campo queda vacio y puede asignarse manualmente
5. **Multi-cliente**: diferentes `sale_partner_id` por linea → validar → verificar separacion en analitica
6. **Templates AvanzOSC con `percentage > 0`**: validar → lineas con `partner_id` y `amount != 0`
7. **Templates con `percentage=0`**: validar → no se crean lineas analiticas inutiles
8. **Proteccion write()** *(v15.0.1.5.6)*: cambiar proveedor (trigger autocomplete) → guardar → verificar que `sale_partner_id` de lineas NO cambia

---

## Seguridad y Permisos

El modulo **NO aniade** nuevos grupos ni reglas de acceso. Utiliza los permisos estandar de:
- `purchase.group_purchase_user`
- `account.group_account_invoice`
- `analytic.group_analytic_accounting`

---

## Instalacion y Configuracion

### Requisitos
- Odoo 15.0
- Modulos: `purchase_stock`, `account`, `analytic`, `account_analytic_distribution`

### Instalacion
```bash
# Actualizar modulo existente
/opt/odoo15_klo/odoo/odoo-bin -c /opt/odoo15_klo/odoo/config/odoo15.conf \
    -u klo_purchase_invoice_final_partner --stop-after-init
```

---

## Troubleshooting

### Problema: El cliente no se propaga a analitica
**Solucion**: Verificar que la factura se valida con `action_post`. Revisar logs para mensajes `KLO PROTECCION`.

### Problema: Al guardar, el `sale_partner_id` de una linea vuelve al valor de la cabecera
**Causa**: El autocompletado de Odoo reescribe las lineas sin incluir `sale_partner_id`.
**Solucion** (v15.0.1.5.6): Cubierto por `AccountMove.write()`. Si ocurre, apareceran mensajes
`WARNING KLO PROTECCION` en los logs indicando que se re-aplico el valor.

### Problema: Al añadir una nueva linea, no aparece el valor por defecto de la cabecera
**Causa posible**: La vista `klo_view_move_invoice_line_context` no esta cargada.
**Diagnostico**: `SELECT name FROM ir_ui_view WHERE name='klo.account.move.invoice.line.context';`
**Solucion**: `-u klo_purchase_invoice_final_partner` para recargar vistas.

### Problema: Nueva linea sobreescribe el valor cambiado manualmente antes de guardar
**Causa**: Version antigua con `not vals.get('sale_partner_id')` en `create()`.
**Solucion** (v15.0.1.5.6): Condicion corregida a `'sale_partner_id' not in vals`. Verificar version.

### Problema: `analytic_account_id` vacio en lineas de factura de compra
**Solucion** (v15.0.1.4.0): Cubierto por override de `_prepare_account_move_line()` y
fallback en `_compute_analytic_account_id()`.

### Problema: Lineas analiticas con `amount=0`
**Causa**: Templates AvanzOSC con `percentage=0.0`.
**Solucion** (v15.0.1.5.2): Eliminadas automaticamente en `action_post()`.
**Solucion definitiva**: Configurar `percentage=100` en `Contabilidad > Configuracion > Plantillas analiticas`.

### Problema: `partner_id` vacio en apuntes analiticos de templates AvanzOSC
**Solucion** (v15.0.1.5.1): Propagado en `action_post()` tras el `super()`.

---

## Changelog

### Version 15.0.1.5.7 (2026-04-30)
- Nuevo: pre-rellenado automatico de `sale_partner_id` en lineas nuevas al añadirlas desde la UI
- Nueva vista `klo_view_move_invoice_line_context`: añade `'default_sale_partner_id': sale_partner_id`
  al contexto del campo `invoice_line_ids`; Odoo base procesa automaticamente los `default_*`
  del contexto en `default_get`, haciendo que la nueva linea aparezca ya con el valor de la cabecera
- Nuevo metodo `AccountMoveLine.default_get()` como fallback para creacion programatica donde
  `default_move_id` este en contexto pero no `default_sale_partner_id`
- Diagnostico del bug: el contexto base de `invoice_line_ids` en Odoo no incluye `default_move_id`,
  por lo que el `default_get` no tenia como obtener el valor de la cabecera sin esta solucion

### Version 15.0.1.5.6 (2026-04-30)
- Nuevo override de `AccountMove.write()` para proteger `sale_partner_id` en lineas contra
  sobreescritura por el autocompletado `_move_autocomplete_invoice_lines_write`
- El override captura los `sale_partner_id` explicitamente enviados (cmd=1 y cmd=0) y los
  re-aplica si el write estandar los perdio; emite `WARNING` en logs cuando actua
- Fix en `AccountMoveLine.create()`: condicion cambiada de `not vals.get('sale_partner_id')`
  a `'sale_partner_id' not in vals` para distinguir "campo no enviado" de "campo enviado con
  cualquier valor incluido False"

### Version 15.0.1.5.5 (2026-04-24)
- Eliminado `@api.onchange('sale_partner_id')` de `account.move` que causaba sobreescritura
  al guardar el formulario con datos parciales de lineas
- Campo `sale_partner_id` en `account.move.line` completamente inerte tras creacion
- Unica propagacion automatica: `create()` con prioridad pedido → cabecera

### Version 15.0.1.5.4 (2026-04-24)
- Eliminado `compute='_compute_sale_partner_id'` de `account.move.line` para evitar recomputes
  automaticos que sobreescribian valores al confirmar la factura

### Version 15.0.1.5.3 (2026-04-24)
- Fix para facturas creadas directamente (sin pedido)
- Añadido `@api.onchange` en `account.move` y override de `create()` en `account.move.line`

### Version 15.0.1.5.2 (2026-04-22)
- Eliminacion automatica en `action_post()` de lineas analiticas de templates con `amount=0`
  y `balance!=0` (generadas por templates con `percentage=0.0`)

### Version 15.0.1.5.1 (2026-04-22)
- Override de `AccountMove.action_post()` para propagar `sale_partner_id` → `partner_id`
  en lineas analiticas del modulo AvanzOSC (`analytic_line_ids`)

### Version 15.0.1.5.0 (2026-04-22)
- Eliminado campo `sale_partner_id` de `account.analytic.line`
- Propagacion al campo estandar `partner_id` en todos los mecanismos analiticos
- Eliminadas vistas de `sale_partner_id` en apuntes analiticos

### Version 15.0.1.4.0 (2026-04-10)
- Override de `_prepare_account_move_line()` con pre-computo de `analytic_account_id`
- Override de `_compute_analytic_account_id()` con fallback al diario

### Version 15.0.1.3.0 (2025-04-10)
- Campos `sale_partner_id` en lineas de pedido y de factura
- Propagacion pedido → factura a nivel de linea

### Versiones Anteriores
- **15.0.1.2.0**: Propagacion a lineas analiticas con distribucion
- **15.0.1.1.0**: Implementacion base, propagacion pedido → factura → analitica

---

## Contribuidores

- **KLO Ingenieria Informatica S.L.L.** — Desarrollo y mantenimiento
- Basado en concepto original de Ecosoft Co., Ltd (2019)

## Soporte

**Contacto**: KLO Ingenieria Informatica S.L.L.
**Website**: https://www.klo.es
**Version del documento**: 2.5
**Fecha**: 2026-04-30

---
*Este documento forma parte de la documentacion tecnica interna de KLO para modulos de Odoo 15.*
