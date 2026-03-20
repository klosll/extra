# Especificación del módulo `klo_account_invoice_uva`

> **Odoo:** 16.0 · **Licencia:** LGPL-3  
> **Autor:** Manuel Calomarde Gomez — KLO Ingenieria Informatica S.L.L.  
> **GitHub:** klosll  
> **Ruta destino:** `/opt/odoo16_desarrollo/odoo/extra-addons/extra/klo_account_invoice_uva`  
> **Dependencia Odoo:** `account`

---

## 1. Reglas globales del proyecto

- Todos los **comentarios del código** deben estar en **español**.
- Los módulos personalizados van en `/opt/odoo16_desarrollo/odoo/extra-addons/extra/`.
- El módulo **NO reinicia Odoo** al terminar: el desarrollador lo hace manualmente.
- El fichero `.gitignore` del repositorio debe excluir `__pycache__/` y `*.pyc`.

---

## 2. Objetivo funcional

Módulo para gestionar **facturas de compra/venta de uva** en Odoo 16.

- Añade cuatro campos decimales en `account.move.line`: `grado`, `kilos`, `precio_kilogrado`, `kilogrados`.
- Añade un campo boolean `es_para_uva` en `account.journal` (solo visible si el diario es de tipo `sale`).
- Cuando ese campo está a `True`, tanto la **vista de formulario** como el **informe QWeb** de la factura cambian automáticamente a versiones especializadas para uva.
- La lógica es **transparente**: se usan los mismos modelos `account.move` y `account.move.line`. Solo cambia la vista y el informe según el diario.

---

## 3. Estructura de ficheros

```
klo_account_invoice_uva/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── account_move_line.py       ← campos grado, kilos, precio_kilogrado, kilogrados + onchange
│   ├── account_journal.py         ← campo es_para_uva + override action_create_new
│   └── account_move.py            ← campo related es_para_uva, get_formview_id,
│                                     _get_name_invoice_report, get_uva_formview_id_for_new
├── views/
│   ├── account_journal_views.xml        ← checkbox es_para_uva en formulario de diario
│   ├── account_move_uva_views.xml       ← vista primaria view_move_form_uva + campo invisible en lista
│   └── report_invoice_uva_wrappers.xml  ← integra el QWeb de uva en los wrappers estándar de impresión
├── report/
│   └── report_invoice_uva.xml     ← template QWeb klo_report_invoice_document_uva
└── static/
    └── src/
        └── js/
            └── account_move_list_open.js  ← patch JS ListController: openRecord + createRecord
```

### Orden de carga en `__manifest__.py → data` (obligatorio)

1. `views/account_journal_views.xml`
2. `views/account_move_uva_views.xml`
3. `report/report_invoice_uva.xml`
4. `views/report_invoice_uva_wrappers.xml`

El asset JS se registra en `assets → web.assets_backend`.

---

## 4. Especificación por fichero

### 4.1 `models/account_move_line.py`

Hereda `account.move.line`. Añade:

| Campo | Tipo | `digits` | Default |
|---|---|---|---|
| `grado` | `Float` | `(16, 2)` | `0.0` |
| `kilos` | `Float` | `(16, 2)` | `0.0` |
| `precio_kilogrado` | `Float` | `(16, 4)` | `0.0` |
| `kilogrados` | `Float` | `(16, 2)` | `0.0` |

**Métodos `@api.onchange`:**

- `_onchange_kilos_grado_uva` → escucha `kilos`, `grado` → recalcula `kilogrados` y `price_unit`
- `_onchange_importe_uva` → escucha `precio_kilogrado`, `kilogrados` → recalcula `price_unit`

Ver fórmulas en [sección 5](#5-fórmulas-de-cálculo).

---

### 4.2 `models/account_journal.py`

Hereda `account.journal`. Añade:

- `es_para_uva`: `Boolean`, `default=False`. Solo visible en la vista si `type == 'sale'`.

Sobrescribe `action_create_new`:
- Si `es_para_uva` es `True` → devuelve un `act_window` con `view_id` apuntando a `view_move_form_uva` y el contexto generado por `self._get_move_action_context()`.
- Si es `False` → llama a `super()`.

---

### 4.3 `models/account_move.py`

Hereda `account.move`. Es el fichero central del módulo. Contiene:

**Campo:**
- `es_para_uva`: `Boolean`, `related='journal_id.es_para_uva'`, **`store=True`**, `readonly=True`.
  - `store=True` es obligatorio para que esté disponible en la vista de lista del cliente JS sin RPC extra.

**Métodos:**

- `get_formview_id(access_uid=None)`: requiere `self.ensure_one()`. Si `journal_id.es_para_uva` → devuelve el ID de `view_move_form_uva`. Si no → `super()`.

- `_get_name_invoice_report()`: requiere `self.ensure_one()`. Si `journal_id.es_para_uva` → devuelve `'klo_account_invoice_uva.klo_report_invoice_document_uva'`. Si no → `super()`.

- `get_uva_formview_id_for_new()`: decorado con `@api.model`. **Nombre público, sin guión bajo inicial** (ver [Error 2](#error-2--método-privado-no-accesible-desde-js)). Lógica:
  1. Lee `default_journal_id` del contexto. Si existe y su `es_para_uva` es `True` → devuelve el ID de `view_move_form_uva`.
  2. Si no hay diario explícito → resuelve el diario predeterminado buscando por `company_id` y tipo (`sale`/`purchase` según `default_move_type` del contexto). Si ese diario tiene `es_para_uva` → devuelve el ID de la vista.
  3. En cualquier otro caso → devuelve `False`.

---

### 4.4 `views/account_journal_views.xml`

Hereda `account.view_account_journal_form`. Inserta el campo `es_para_uva` con `widget="boolean_toggle"` después del campo `type`, con `attrs` para ocultarlo cuando `type != 'sale'`.

---

### 4.5 `views/account_move_uva_views.xml`

Contiene **dos registros**:

**A) `view_move_form_uva`**
- Modelo: `account.move`
- `inherit_id`: `account.view_move_form`
- **`mode="primary"`** → independiente de la vista estándar; no la modifica.
- Modificaciones en las columnas del tree de `invoice_line_ids`:

| Columna original | Acción | Resultado |
|---|---|---|
| `name` (widget `section_and_note_text`) | `optional=hide` | Oculta por defecto |
| `account_id` | `optional=hide` | Oculta por defecto |
| `quantity` (con atributo `@optional`) | `optional=hide` | Oculta por defecto |
| Antes de `price_unit` | `position="before"` | Inserta `grado`, `kilos`, `precio_kilogrado`, `kilogrados` con `optional="show"` |
| `price_unit` | `string="Importe"` | Renombrada, visible |
| `tax_ids` (widget `many2many_tags`) | `optional=hide` | Oculta por defecto |

**B) `view_invoice_list_es_para_uva`**
- Hereda `account.view_invoice_tree`.
- Añade `es_para_uva` con `invisible="1"` después de `move_type`.
- Propósito: que el dato esté disponible en `record.data` del cliente JS sin RPC adicional.

---

### 4.6 `report/report_invoice_uva.xml`

Template QWeb con:
- `id="klo_report_invoice_document_uva"`
- `inherit_id="account.report_invoice_document"`
- `primary="True"`

> ⚠️ Debe ir directamente bajo `<odoo>` **sin** bloque `<data>` (ver [Error 1](#error-1--schema-xml-inválido)).

Modificaciones sobre el template estándar:

| Elemento modificado | Acción |
|---|---|
| `th_description/span` | Texto → `"Descripción"` |
| `th_quantity` | Reemplazado por 4 `<th>`: `Grado (°)`, `Kilos`, `€/Kilogrado`, `Kilogrados` |
| `th_priceunit/span` | Texto → `"Importe"` |
| `th_taxes` | Reemplazado por `<th/>` vacío |
| `th_subtotal` | `style="display:none;"` |
| `t[@name='account_invoice_line_accountable']` | Reemplazado: muestra `line.name`, `line.grado`, `line.kilos`, `line.precio_kilogrado`, `line.kilogrados` y `line.price_subtotal`/`line.price_total` según grupo fiscal |

---

### 4.7 `views/report_invoice_uva_wrappers.xml`

Herencias de dos wrappers estándar, dentro de `<data>`:

- `account.report_invoice`
- `account.report_invoice_with_payments`

En ambos, tras el `<t t-if>` existente se añade un `<t t-elif>` que evalúa si `o._get_name_invoice_report()` devuelve el nombre del template de uva y, en ese caso, lo renderiza con `t-call` y `t-lang`.

> ℹ️ Las herencias de templates sí van dentro de `<data>`. Solo los templates `primary` van fuera.

---

### 4.8 `static/src/js/account_move_list_open.js`

Patch de `ListController` usando `patch` de `@web/core/utils/patch` y `ListController` de `@web/views/list/list_controller`.

Nombre del patch: `"klo_account_invoice_uva.list_controller_open_record"`.

**Método `openRecord(record)`** (async):
- Solo actúa si `this.props.resModel === "account.move"` y `record.data.es_para_uva === true`.
- Llama a `this.orm.call("account.move", "get_formview_action", [[record.resId]])`.
- Añade al contexto de la acción: `active_id`, `active_ids` (todos los resIds del listado actual), `active_model`.
- Ejecuta `this.actionService.doAction(action)`.
- Si no aplica → llama a `superFn(record)`.

**Método `createRecord()`** (async):
- Solo actúa si `this.props.resModel === "account.move"`.
- Llama a `this.orm.call("account.move", "get_uva_formview_id_for_new", [], { context: this.props.context })`.
- Si devuelve un `viewId` → ejecuta `this.actionService.doAction` con `type: "ir.actions.act_window"`, `views: [[viewId, "form"]]`, `context: this.props.context`.
- Si devuelve `false` → llama a `superFn()`.

> ⚠️ **Regla crítica:** en ambos métodos `async`, guardar `const superFn = this._super.bind(this)` **antes del primer `await`** (ver [Error 3](#error-3--_super-no-disponible-en-método-async)).

---

## 5. Fórmulas de cálculo

```
kilogrados = kilos × grado
             → onchange: kilos, grado

price_unit = precio_kilogrado × kilogrados × 1000
             → onchange: kilos, grado  (encadenado, tras recalcular kilogrados)
             → onchange: precio_kilogrado, kilogrados
```

---

## 6. Flujos de la aplicación

### Crear factura desde el dashboard (kanban del diario)

```
Pulsar "+" en el diario
  → account.journal.action_create_new()
  → Si es_para_uva: act_window con view_id = view_move_form_uva
  → Si no: flujo estándar de Odoo
```

### Crear factura desde la lista

```
Pulsar "Nuevo" en la lista de facturas
  → createRecord() del patch JS
  → ORM: account.move.get_uva_formview_id_for_new()
  → Si devuelve viewId: doAction con views: [[viewId, "form"]]
  → Si no: superFn() → flujo estándar
```

### Editar factura existente desde la lista

```
Clic en una fila de la lista
  → openRecord() del patch JS
  → Comprueba record.data.es_para_uva (disponible sin RPC gracias al campo invisible en la lista)
  → Si True: ORM account.move.get_formview_action([resId])
             → internamente llama a get_formview_id() → devuelve view_move_form_uva
             → doAction con la acción recibida
  → Si False: superFn() → flujo estándar
```

### Imprimir factura

```
Pulsar "Imprimir"
  → Odoo evalúa wrapper account.report_invoice
  → t-elif comprueba o._get_name_invoice_report()
  → Si devuelve el nombre del template UVA: renderiza klo_report_invoice_document_uva
  → Si no: flujo estándar
```

---

## 7. Errores conocidos y sus soluciones

### Error 1 — Schema XML inválido

```
ERROR odoo.tools.convert: The XML file 'report/report_invoice_uva.xml'
does not fit the required schema!
```

**Causa:** El template QWeb `primary` estaba dentro de `<data>`.  
**Solución:** Los templates `primary` deben ir directamente bajo `<odoo>`, sin `<data>`.

---

### Error 2 — Método privado no accesible desde JS

```
AccessError: Private methods (such as 'account.move._get_uva_formview_id_for_new')
cannot be called remotely.
```

**Causa:** El método empezaba con guión bajo (`_`).  
**Solución:** El método debe ser público: `get_uva_formview_id_for_new` (sin guión bajo).

---

### Error 3 — `_super` no disponible en método async

```
UncaughtPromiseError > TypeError: this._super is not a function
  at createRecord (account_move_list_open.js)
```

**Causa:** El mecanismo `patch()` de Odoo 16 restaura `this._super` síncronamente al recibir la `Promise` que devuelve la función `async`. Cuando el código se reanuda tras el primer `await`, `_super` ya no está disponible.  
**Solución:** Guardar `const superFn = this._super.bind(this)` **antes del primer `await`**, en todos los métodos async parcheados.

---

### Error 4 — `get_formview_id` no se invoca al abrir desde la lista

**Causa:** El `ListController` de Odoo 16 llama a `openRecord` sin pasar por `get_formview_id` del servidor.  
**Solución combinada:**
1. Patch JS de `openRecord` que llama explícitamente a `get_formview_action` (que sí usa `get_formview_id`).
2. `es_para_uva` debe existir en `record.data` → se consigue añadiéndolo como `invisible="1"` en `view_invoice_tree` y con `store=True` en el campo related de `account.move`.
