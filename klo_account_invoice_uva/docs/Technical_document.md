# Documentación Técnica - Módulo klo_account_invoice_uva

## Información General

**Nombre del módulo:** `klo_account_invoice_uva`  
**Versión:** 16.0.1.0.0  
**Categoría:** Accounting/Accounting  
**Autor:** Manuel Calomarde Gomez - KLO Ingenieria Informatica S.L.L.  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 16.0  

---

## 1. Propósito del Módulo

Este módulo especializa la gestión de facturas de compra/venta de uva en Odoo 16, añadiendo campos específicos del sector vinícola:

- **Grado (°):** Graduación alcohólica de la uva
- **Kilos:** Peso de la uva
- **€/Kilogrado:** Precio por kilogrado
- **Kilogrados:** Resultado del cálculo Kilos × Grado

El módulo modifica dinámicamente la vista de factura y el reporte PDF cuando el diario está marcado como "Es para uva", sin afectar al funcionamiento estándar de facturas normales.

---

## 2. Dependencias

```python
'depends': ['account']
```

El módulo depende únicamente del módulo core `account` de Odoo.

---

## 3. Estructura del Módulo

```
klo_account_invoice_uva/
├── __init__.py
├── __manifest__.py
├── data/
│   └── decimal_precision.xml
├── models/
│   ├── __init__.py
│   ├── account_journal.py
│   ├── account_move.py
│   └── account_move_line.py
├── views/
│   ├── account_journal_views.xml
│   ├── account_move_uva_views.xml
│   └── report_invoice_uva_wrappers.xml
├── report/
│   └── report_invoice_uva.xml
├── static/
│   └── src/
│       └── js/
│           └── account_move_list_open.js
└── docs/
    ├── fix_alineacion_importe.md
    └── Technical_document.md
```

---

## 4. Modelos y Campos Personalizados

### 4.1. account.journal (Diarios Contables)

**Archivo:** `models/account_journal.py`

#### Campos Añadidos

```python
es_para_uva = fields.Boolean(
    string='Es para uva',
    default=False,
    help='Si está marcado, al crear una nueva factura desde el dashboard '
         'se utilizará la vista especializada para facturas de uva.',
)
```

**Características:**
- Tipo: Boolean
- Valor por defecto: False
- Visible solo en diarios de tipo 'sale' (ventas)
- Widget: `boolean_toggle` (interruptor visual)

#### Métodos Sobrescritos

##### `action_create_new()`

**Propósito:** Intercepta la creación de facturas desde el dashboard del diario.

**Lógica:**
```python
def action_create_new(self):
    if self.es_para_uva:
        return {
            'name': _('Crear factura de uva'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('klo_account_invoice_uva.view_move_form_uva').id,
            'context': self._get_move_action_context(),
        }
    return super().action_create_new()
```

**Comportamiento:**
- Si `es_para_uva == True`: Abre `view_move_form_uva` (vista especializada)
- Si `es_para_uva == False`: Ejecuta el comportamiento estándar de Odoo

---

### 4.2. account.move (Facturas/Asientos Contables)

**Archivo:** `models/account_move.py`

#### Campos Añadidos

```python
es_para_uva = fields.Boolean(
    string='Es factura de uva',
    related='journal_id.es_para_uva',
    store=True,
    readonly=True,
)
```

**Características:**
- Campo relacionado (computed) desde `journal_id.es_para_uva`
- Almacenado en BD (`store=True`) para:
  - Usarlo en filtros y búsquedas
  - Disponerlo en vistas de lista sin llamadas extra al servidor
- Solo lectura (se actualiza automáticamente cuando cambia el diario)

#### Métodos Sobrescritos

##### `get_formview_id(access_uid=None)`

**Propósito:** Define qué vista de formulario usar al abrir/editar una factura existente.

**Lógica:**
```python
def get_formview_id(self, access_uid=None):
    self.ensure_one()
    if self.journal_id.es_para_uva:
        return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
    return super().get_formview_id(access_uid=access_uid)
```

**Comportamiento:**
- Si el diario tiene `es_para_uva == True`: Devuelve el ID de `view_move_form_uva`
- Si no: Ejecuta el comportamiento estándar (vista por defecto según tipo de factura)

**Cuándo se llama:**
- Al hacer clic en una factura existente desde cualquier vista de lista
- Al navegar entre registros con los botones ◀ ▶

---

##### `_get_name_invoice_report()`

**Propósito:** Selecciona el template QWeb para la impresión/PDF de la factura.

**Lógica:**
```python
def _get_name_invoice_report(self):
    self.ensure_one()
    if self.journal_id.es_para_uva:
        return 'klo_account_invoice_uva.klo_report_invoice_document_uva'
    return super()._get_name_invoice_report()
```

**Comportamiento:**
- Si `es_para_uva == True`: Usa el template personalizado `klo_report_invoice_document_uva`
- Si no: Usa el template estándar `account.report_invoice_document`

**Cuándo se llama:**
- Al pulsar el botón "Imprimir" en la factura
- Al generar el PDF desde el portal del cliente
- Al enviar la factura por email (PDF adjunto)

---

##### `get_uva_formview_id_for_new()` [Método de modelo @api.model]

**Propósito:** Determina si una nueva factura (sin crear aún) debe usar la vista de uva.

**Firma:**
```python
@api.model
def get_uva_formview_id_for_new(self):
    # ...lógica de resolución del diario...
```

**Lógica de Resolución del Diario:**

1. **Diario explícito en contexto:**
   ```python
   journal_id = self._context.get('default_journal_id')
   if journal_id:
       journal = self.env['account.journal'].browse(journal_id)
       if journal.es_para_uva:
           return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
       return False
   ```

2. **Diario predeterminado según tipo de movimiento:**
   ```python
   move_type = self._context.get('default_move_type', 'entry')
   if move_type in ('out_invoice', 'out_refund', 'out_receipt'):
       journal_types = ['sale']
   elif move_type in ('in_invoice', 'in_refund', 'in_receipt'):
       journal_types = ['purchase']
   else:
       return False
   
   journal = self.env['account.journal'].search(
       [('company_id', '=', company_id), ('type', 'in', journal_types)],
       limit=1,
   )
   if journal and journal.es_para_uva:
       return self.env.ref('klo_account_invoice_uva.view_move_form_uva').id
   return False
   ```

**Retorno:**
- `int`: ID de la vista `view_move_form_uva` si procede usar la vista de uva
- `False`: Si debe usarse la vista estándar

**Cuándo se llama:**
- Desde JavaScript antes de crear un nuevo registro
- Solo cuando se hace clic en "Crear" desde una vista de lista de facturas

---

### 4.3. account.move.line (Líneas de Factura)

**Archivo:** `models/account_move_line.py`

#### Campos Añadidos

```python
grado = fields.Float(
    string='Grado',
    digits=(16, 2),
    default=0.0,
)

kilos = fields.Float(
    string='Kilos',
    digits=(16, 2),
    default=0.0,
)

precio_kilogrado = fields.Float(
    string='€/Kilogrado',
    digits='Precio Kilogrado',  # 5 decimales (ver decimal_precision.xml)
    default=0.0,
)

kilogrados = fields.Float(
    string='Kilogrados',
    digits='Kilogrados',  # 0 decimales (ver decimal_precision.xml)
    default=0.0,
)
```

**Precisión Decimal:**
- `grado`: 16 dígitos, 2 decimales (estándar Float)
- `kilos`: 16 dígitos, 2 decimales (estándar Float)
- `precio_kilogrado`: 5 decimales (referencia a `decimal.precision`)
- `kilogrados`: 0 decimales (referencia a `decimal.precision`)

#### Métodos OnChange

##### `_onchange_kilos_grado_uva()`

**Decorador:**
```python
@api.onchange('kilos', 'grado')
```

**Propósito:** Recalcula automáticamente `kilogrados` y `price_unit` cuando cambian los kilos o el grado.

**Fórmulas:**
```python
self.kilogrados = self.kilos * self.grado
self.price_unit = self.precio_kilogrado * self.kilogrados
```

**Comportamiento:**
1. Usuario modifica `kilos` o `grado` en la interfaz
2. Se calcula automáticamente `kilogrados = kilos × grado`
3. Se recalcula el importe: `price_unit = €/kilogrado × kilogrados`
4. Los cambios se reflejan inmediatamente en la interfaz (sin guardar)

---

##### `_onchange_importe_uva()`

**Decorador:**
```python
@api.onchange('precio_kilogrado', 'kilogrados')
```

**Propósito:** Recalcula el importe (`price_unit`) cuando cambia el precio por kilogrado o los kilogrados.

**Fórmula:**
```python
self.price_unit = self.precio_kilogrado * self.kilogrados
```

**Comportamiento:**
1. Usuario modifica `precio_kilogrado` o `kilogrados` en la interfaz
2. Se recalcula automáticamente `price_unit = €/kilogrado × kilogrados`
3. El cambio se refleja inmediatamente en la columna "Importe"

**Nota:** En la descripción original del módulo se mencionaba la fórmula `€/kilogrado × Kilogrados × 1.000`, pero en la implementación actual se usa `€/kilogrado × Kilogrados` directamente. Si se requiere el factor 1.000, modificar esta línea.

---

## 5. Vistas XML

### 5.1. Vista de Diario (account_journal_views.xml)

**ID de Vista:** `view_account_journal_form_uva`

**Hereda de:** `account.view_account_journal_form`

**Modificación:**
```xml
<xpath expr="//field[@name='type']" position="after">
    <field name="es_para_uva"
           attrs="{'invisible': [('type', '!=', 'sale')]}"
           widget="boolean_toggle"/>
</xpath>
```

**Características:**
- Añade el campo `es_para_uva` después del campo `type`
- Solo visible cuando el tipo de diario es 'sale' (ventas)
- Widget de interruptor visual (toggle) para mejor UX

---

### 5.2. Vista de Factura para Uva (account_move_uva_views.xml)

#### Vista Formulario: `view_move_form_uva`

**ID de Vista:** `view_move_form_uva`  
**Modelo:** `account.move`  
**Hereda de:** `account.view_move_form`  
**Modo:** `primary` (vista independiente, no afecta a la estándar)

**Modificaciones en las Líneas de Factura (invoice_line_ids):**

##### Columnas Ocultas por Defecto (`optional="hide"`):
1. **Etiqueta** (`name` con widget `section_and_note_text`)
2. **Cuenta** (`account_id`)
3. **Cantidad** (`quantity`)
4. **Impuestos** (`tax_ids` con widget `many2many_tags`)

##### Columnas Añadidas (visibles por defecto, `optional="show"`):
Se insertan **antes** de `price_unit`:
```xml
<field name="grado" string="Grado" optional="show"/>
<field name="kilos" string="Kilos" optional="show"/>
<field name="precio_kilogrado" string="€/kilogrado" optional="show"/>
<field name="kilogrados" string="Kilogrados" optional="show"/>
```

##### Columna Renombrada:
```xml
<field name="price_unit">
    <attribute name="string">Importe</attribute>
</field>
```
El campo `price_unit` (Precio Unitario) se renombra a "Importe" en la vista de uva.

**Orden Final de Columnas Visibles:**
1. Producto/Descripción
2. **Grado** ✓
3. **Kilos** ✓
4. **€/kilogrado** ✓
5. **Kilogrados** ✓
6. **Importe** (price_unit renombrado) ✓
7. Subtotal (price_subtotal)

---

#### Vista Lista con Campo Invisible: `view_invoice_list_es_para_uva`

**ID de Vista:** `view_invoice_list_es_para_uva`  
**Modelo:** `account.move`  
**Hereda de:** `account.view_invoice_tree`

**Propósito:** Añadir el campo `es_para_uva` como invisible en todas las listas de facturas.

**Modificación:**
```xml
<xpath expr="//field[@name='move_type']" position="after">
    <field name="es_para_uva" invisible="1"/>
</xpath>
```

**Importancia:**
- El campo invisible **no se muestra como columna** pero sus datos se cargan en el cliente
- El JavaScript del parche `ListController` puede leer `record.data.es_para_uva` directamente
- Evita llamadas AJAX adicionales al servidor al abrir facturas desde la lista

---

### 5.3. Precisión Decimal (decimal_precision.xml)

**Archivo:** `data/decimal_precision.xml`  
**Atributo:** `noupdate="1"` (no se sobrescribe en actualizaciones del módulo)

#### Registros Creados:

##### Precisión "Precio Kilogrado":
```xml
<record forcecreate="True" id="decimal_precision_precio_kilogrado" model="decimal.precision">
    <field name="name">Precio Kilogrado</field>
    <field name="digits">5</field>
</record>
```
- **Uso:** Campo `precio_kilogrado` en `account.move.line`
- **Decimales:** 5 (ejemplo: 0.12345 €/kg°)

##### Precisión "Kilogrados":
```xml
<record forcecreate="True" id="decimal_precision_kilogrados" model="decimal.precision">
    <field name="name">Kilogrados</field>
    <field name="digits">0</field>
</record>
```
- **Uso:** Campo `kilogrados` en `account.move.line`
- **Decimales:** 0 (número entero, ejemplo: 1234 kg°)

**Nota:** El atributo `forcecreate="True"` asegura que los registros se crean incluso si ya existen en la base de datos.

---

## 6. Reporte QWeb (PDF de Factura)

### 6.1. Template Principal: `klo_report_invoice_document_uva`

**Archivo:** `report/report_invoice_uva.xml`  
**ID:** `klo_report_invoice_document_uva`  
**Hereda de:** `account.report_invoice_document`  
**Modo:** `primary="True"` (template independiente)

#### Estructura de Columnas en el PDF:

| # | Columna          | Campo QWeb              | Alineación | Notas                          |
|---|------------------|-------------------------|------------|--------------------------------|
| 1 | Descripción      | `line.name`             | Izquierda  | Producto/variedad de uva       |
| 2 | Grado (°)        | `line.grado`            | Derecha    | Graduación alcohólica          |
| 3 | Kilos            | `line.kilos`            | Derecha    | Peso                           |
| 4 | €/Kilogrado      | `line.precio_kilogrado` | Derecha    | Precio unitario (5 decimales)  |
| 5 | Kilogrados       | `line.kilogrados`       | Derecha    | Kilos × Grado (0 decimales)    |
| 6 | Importe          | `line.price_subtotal` o `line.price_total` | Derecha | Total línea |

#### Modificaciones en las Cabeceras (thead):

##### Cabecera "Description" → "Descripción":
```xml
<xpath expr="//th[@name='th_description']/span" position="replace">
    <span>Descripción</span>
</xpath>
```

##### Cabecera "Quantity" → 4 columnas UVA:
```xml
<xpath expr="//th[@name='th_quantity']" position="replace">
    <th name="th_grado" class="text-end"><span>Grado (°)</span></th>
    <th name="th_kilos" class="text-end"><span>Kilos</span></th>
    <th name="th_precio_kilogrado" class="text-end"><span>€/Kilogrado</span></th>
    <th name="th_kilogrados" class="text-end"><span>Kilogrados</span></th>
</xpath>
```

##### Eliminación de Columnas Innecesarias:
```xml
<!-- Eliminar "Unit Price" -->
<xpath expr="//th[@name='th_priceunit']" position="replace"/>

<!-- Eliminar "Disc.%" (descuento) -->
<xpath expr="//th[@name='th_price_unit']" position="replace"/>

<!-- Eliminar "Taxes" -->
<xpath expr="//th[@name='th_taxes']" position="replace"/>
```

##### Cabecera "Amount/Total Price" → "Importe":
```xml
<xpath expr="//th[@name='th_subtotal']/span" position="replace">
    <span>Importe</span>
</xpath>
```

**Importante:** Se reutiliza la columna `th_subtotal` original cambiando solo su etiqueta. Esto asegura la correcta alineación con los totales del pie del documento.

---

#### Modificaciones en las Celdas de Datos (tbody):

Se reemplaza completamente el bloque `account_invoice_line_accountable`:

```xml
<xpath expr="//t[@name='account_invoice_line_accountable']" position="replace">
    <t t-if="line.display_type == 'product'" name="account_invoice_line_accountable">
        
        <!-- Descripción -->
        <td name="account_invoice_line_name">
            <span t-field="line.name" t-options="{'widget': 'text'}"/>
        </td>
        
        <!-- Grado -->
        <td class="text-end">
            <span t-field="line.grado"/>
        </td>
        
        <!-- Kilos -->
        <td class="text-end">
            <span t-field="line.kilos"/>
        </td>
        
        <!-- €/Kilogrado -->
        <td class="text-end">
            <span t-field="line.precio_kilogrado"/>
        </td>
        
        <!-- Kilogrados -->
        <td class="text-end">
            <span t-field="line.kilogrados"/>
        </td>
        
        <!-- Importe (columna th_subtotal) -->
        <td class="text-end o_price_total">
            <span class="text-nowrap" t-field="line.price_subtotal"
                  groups="account.group_show_line_subtotals_tax_excluded"/>
            <span class="text-nowrap" t-field="line.price_total"
                  groups="account.group_show_line_subtotals_tax_included"/>
        </td>
        
    </t>
</xpath>
```

**Características:**
- Exactamente 6 columnas `<td>` que coinciden con las 6 cabeceras `<th>`
- Clase `o_price_total` en la última columna para estilo consistente
- Respeta la configuración fiscal del usuario (`tax_excluded` vs `tax_included`)

---

### 6.2. Wrappers del Reporte (report_invoice_uva_wrappers.xml)

#### Template: `klo_inherit_report_invoice`

**Hereda de:** `account.report_invoice`

**Propósito:** Interceptar la generación del PDF estándar y usar el template de uva cuando proceda.

```xml
<template id="klo_inherit_report_invoice" inherit_id="account.report_invoice">
    <xpath expr="//t[@t-if]" position="after">
        <t t-elif="o._get_name_invoice_report() == 'klo_account_invoice_uva.klo_report_invoice_document_uva'"
           t-call="klo_account_invoice_uva.klo_report_invoice_document_uva"
           t-lang="lang"/>
    </xpath>
</template>
```

**Funcionamiento:**
1. Odoo llama a `o._get_name_invoice_report()` (método sobrescrito en `account.move`)
2. Si devuelve `'klo_account_invoice_uva.klo_report_invoice_document_uva'`:
   - Se renderiza el template de uva
3. Si no:
   - Se usa el template estándar de Odoo

---

#### Template: `klo_inherit_report_invoice_with_payments`

**Hereda de:** `account.report_invoice_with_payments`

**Propósito:** Mismo comportamiento para el reporte con pagos registrados.

```xml
<template id="klo_inherit_report_invoice_with_payments" inherit_id="account.report_invoice_with_payments">
    <xpath expr="//t[@t-if]" position="after">
        <t t-elif="o._get_name_invoice_report() == 'klo_account_invoice_uva.klo_report_invoice_document_uva'"
           t-call="klo_account_invoice_uva.klo_report_invoice_document_uva"
           t-lang="lang"/>
    </xpath>
</template>
```

---

## 7. JavaScript (Frontend)

### 7.1. Parche del ListController

**Archivo:** `static/src/js/account_move_list_open.js`  
**Módulo Odoo:** `@odoo-module`

#### Propósito General

Interceptar la apertura y creación de facturas desde vistas de lista para usar automáticamente la vista de uva cuando el diario lo requiera.

#### Importaciones

```javascript
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
```

---

#### Parche Aplicado

```javascript
patch(ListController.prototype, "klo_account_invoice_uva.list_controller_open_record", {
    // Métodos sobrescritos...
});
```

---

#### Método: `openRecord(record)` - EDITAR FACTURA EXISTENTE

**Propósito:** Al hacer clic en una factura existente desde una lista, abrir la vista de uva si corresponde.

**Código:**
```javascript
async openRecord(record) {
    // Guardar _super ANTES del primer await (ver explicación más abajo)
    const superFn = this._super.bind(this);

    if (this.props.resModel === "account.move" && record.data.es_para_uva) {
        // Llamar a get_formview_action → get_formview_id → view_move_form_uva
        const action = await this.orm.call(
            "account.move",
            "get_formview_action",
            [[record.resId]],
        );
        
        // Propagar los resIds activos para navegación entre registros
        const activeIds = this.model.root.records.map((dp) => dp.resId);
        action.context = {
            ...action.context,
            active_id: record.resId,
            active_ids: activeIds,
            active_model: "account.move",
        };
        
        return this.actionService.doAction(action);
    }
    
    // Comportamiento estándar para facturas normales y otros modelos
    return superFn(record);
}
```

**Flujo de Ejecución:**
1. Usuario hace clic en una factura en la lista
2. JavaScript comprueba si `this.props.resModel === "account.move"` (es una factura)
3. Lee `record.data.es_para_uva` (campo invisible cargado en la lista)
4. Si es `true`:
   - Llama a `get_formview_action` en el servidor
   - El servidor ejecuta `get_formview_id()` → devuelve ID de `view_move_form_uva`
   - Abre la acción con la vista de uva
5. Si es `false`:
   - Ejecuta el comportamiento estándar de Odoo

**Ventaja:** No requiere llamadas extra al servidor porque `es_para_uva` ya está en `record.data`.

---

#### Método: `createRecord()` - CREAR NUEVA FACTURA

**Propósito:** Al hacer clic en "Crear" desde una lista de facturas, abrir la vista de uva si el diario predeterminado lo requiere.

**Código:**
```javascript
async createRecord() {
    // Guardar _super ANTES del primer await
    const superFn = this._super.bind(this);

    if (this.props.resModel === "account.move") {
        const viewId = await this.orm.call(
            "account.move",
            "get_uva_formview_id_for_new",
            [],
            { context: this.props.context },
        );
        
        if (viewId) {
            // Abrir el formulario de uva para un nuevo registro
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "account.move",
                view_mode: "form",
                views: [[viewId, "form"]],
                target: "current",
                context: this.props.context,
            });
        }
    }
    
    // Comportamiento estándar
    return superFn();
}
```

**Flujo de Ejecución:**
1. Usuario hace clic en "Crear" desde una lista de facturas
2. JavaScript llama al método `get_uva_formview_id_for_new()` en el servidor
3. El servidor:
   - Resuelve el diario que se usará (según contexto)
   - Comprueba si `es_para_uva == True`
   - Devuelve el ID de `view_move_form_uva` o `False`
4. Si devuelve un `viewId`:
   - JavaScript abre directamente la vista de uva
5. Si devuelve `False`:
   - Se ejecuta el comportamiento estándar de Odoo

---

#### Nota Técnica Importante: `this._super` en Métodos Async

**Problema:**
El mecanismo de patch de Odoo 16 configura `this._super` de forma síncrona y lo restaura inmediatamente después del retorno de la función parcheada. En funciones `async`, el retorno es una `Promise`, por lo que `this._super` se restaura **ANTES** de que el código async termine.

**Solución:**
Guardar `this._super` en una variable local **ANTES** del primer `await`:

```javascript
async openRecord(record) {
    // ✅ CORRECTO: Guardar _super antes del await
    const superFn = this._super.bind(this);
    
    const result = await this.orm.call(...);
    
    // ✅ Usar superFn en lugar de this._super
    return superFn(record);
}

// ❌ INCORRECTO:
async openRecord(record) {
    const result = await this.orm.call(...);
    
    // ⚠️ this._super ya no existe aquí!
    return this._super(record);  // ERROR: this._super is not a function
}
```

---

## 8. Flujo de Trabajo Completo

### 8.1. Configuración Inicial

1. **Instalar el módulo** `klo_account_invoice_uva`
2. **Ir a:** Contabilidad → Configuración → Diarios
3. **Seleccionar/crear** un diario de tipo "Ventas" (sale)
4. **Marcar el campo** "Es para uva" ✓
5. **Guardar** el diario

### 8.2. Crear Factura de Uva desde el Dashboard

**Ruta:** Contabilidad → Dashboard → (Diario de uva) → Botón "Crear"

**Flujo Técnico:**
1. Usuario hace clic en el botón de crear del diario
2. Se ejecuta `account.journal.action_create_new()`
3. Como `es_para_uva == True`:
   - Se abre `view_move_form_uva`
   - Las columnas UVA (Grado, Kilos, etc.) están visibles
   - El campo "Cantidad" está oculto

**Interacción del Usuario:**
1. Rellenar datos de cabecera (Cliente, Fecha, etc.)
2. Añadir línea de factura:
   - Producto/Descripción: "Uva Tempranillo"
   - **Grado:** 13.50
   - **Kilos:** 25000.00
   - **€/Kilogrado:** 0.00234 (5 decimales)
3. Al modificar Grado o Kilos:
   - Se calcula automáticamente **Kilogrados** = 25000 × 13.5 = 337500 kg°
   - Se calcula automáticamente **Importe** = 0.00234 × 337500 = 789.75 €
4. Guardar y confirmar la factura

### 8.3. Crear Factura de Uva desde Lista de Facturas

**Ruta:** Contabilidad → Clientes → Facturas → Botón "Crear"

**Flujo Técnico:**
1. Usuario hace clic en "Crear"
2. Se ejecuta el parche JavaScript `createRecord()`
3. JavaScript llama a `account.move.get_uva_formview_id_for_new()`
4. El servidor resuelve el diario predeterminado:
   - Si `default_journal_id` en contexto → usa ese diario
   - Si no → busca el primer diario de tipo "sale"
5. Si el diario tiene `es_para_uva == True`:
   - Devuelve el ID de `view_move_form_uva`
   - JavaScript abre la vista de uva
6. Si no:
   - Devuelve `False`
   - JavaScript abre la vista estándar

### 8.4. Editar Factura de Uva Existente

**Ruta:** Contabilidad → Clientes → Facturas → (clic en factura de uva)

**Flujo Técnico:**

#### Opción A: Desde Vista de Lista (con parche JS)
1. Usuario hace clic en la factura
2. Se ejecuta el parche JavaScript `openRecord(record)`
3. JavaScript lee `record.data.es_para_uva` (campo invisible)
4. Si es `true`:
   - Llama a `get_formview_action()` que internamente usa `get_formview_id()`
   - El servidor devuelve una acción con `view_move_form_uva`
   - Se abre la vista de uva
5. Si es `false`:
   - Se abre la vista estándar

#### Opción B: Apertura Directa (sin parche JS)
1. Usuario accede directamente a la URL de la factura
2. Odoo llama a `account.move.get_formview_id()`
3. Si `journal_id.es_para_uva == True`:
   - Devuelve el ID de `view_move_form_uva`
4. Si no:
   - Devuelve la vista estándar según `super()`

### 8.5. Imprimir/Generar PDF de Factura de Uva

**Ruta:** (Dentro de la factura) → Botón "Imprimir"

**Flujo Técnico:**
1. Usuario hace clic en "Imprimir"
2. Odoo llama a `account.move._get_name_invoice_report()`
3. Si `journal_id.es_para_uva == True`:
   - Devuelve `'klo_account_invoice_uva.klo_report_invoice_document_uva'`
4. El sistema de reportes busca el wrapper `report_invoice`
5. El wrapper compara el nombre devuelto:
   ```xml
   <t t-elif="o._get_name_invoice_report() == 'klo_account_invoice_uva.klo_report_invoice_document_uva'"
      t-call="klo_account_invoice_uva.klo_report_invoice_document_uva" .../>
   ```
6. Se renderiza el template de uva con las columnas personalizadas
7. Se genera el PDF y se descarga

**Resultado en el PDF:**
```
┌──────────────┬──────┬────────┬─────────────┬───────────┬──────────┐
│ Descripción  │ Grado│ Kilos  │ €/Kilogrado │ Kilogrados│ Importe  │
├──────────────┼──────┼────────┼─────────────┼───────────┼──────────┤
│ Uva Tempran. │ 13.5 │ 25000  │ 0.00234     │ 337500    │ 789.75 € │
└──────────────┴──────┴────────┴─────────────┴───────────┴──────────┘
```

---

## 9. Consideraciones Técnicas para IAs

### 9.1. Modificar Fórmulas de Cálculo

**Ubicación:** `models/account_move_line.py`

**Ejemplo:** Añadir el factor 1.000 en el cálculo del importe:

```python
@api.onchange('precio_kilogrado', 'kilogrados')
def _onchange_importe_uva(self):
    # Fórmula: Importe = €/kilogrado × Kilogrados × 1.000
    self.price_unit = self.precio_kilogrado * self.kilogrados * 1000
```

**Importante:** También hay que modificar el otro `@api.onchange`:

```python
@api.onchange('kilos', 'grado')
def _onchange_kilos_grado_uva(self):
    self.kilogrados = self.kilos * self.grado
    # Aplicar el mismo factor 1.000
    self.price_unit = self.precio_kilogrado * self.kilogrados * 1000
```

---

### 9.2. Añadir Nuevos Campos a las Líneas

**Pasos:**

1. **Definir el campo en `account.move.line`:**
   ```python
   # models/account_move_line.py
   nuevo_campo = fields.Float(string='Nuevo Campo', digits=(16, 2))
   ```

2. **Añadir a la vista de formulario:**
   ```xml
   <!-- views/account_move_uva_views.xml -->
   <xpath expr="//field[@name='precio_kilogrado']" position="after">
       <field name="nuevo_campo" string="Nuevo Campo" optional="show"/>
   </xpath>
   ```

3. **Añadir al reporte PDF:**
   ```xml
   <!-- report/report_invoice_uva.xml -->
   
   <!-- En las cabeceras -->
   <xpath expr="//th[@name='th_kilogrados']" position="after">
       <th name="th_nuevo_campo" class="text-end"><span>Nuevo Campo</span></th>
   </xpath>
   
   <!-- En las celdas de datos -->
   <xpath expr="//td[span[@t-field='line.kilogrados']]" position="after">
       <td class="text-end">
           <span t-field="line.nuevo_campo"/>
       </td>
   </xpath>
   ```

4. **Actualizar el módulo:**
   ```bash
   odoo-bin -u klo_account_invoice_uva -d database_name
   ```

---

### 9.3. Cambiar Precisión Decimal de Campos Existentes

**Ubicación:** `data/decimal_precision.xml`

**Ejemplo:** Cambiar `precio_kilogrado` de 5 a 6 decimales:

```xml
<record forcecreate="True" id="decimal_precision_precio_kilogrado" model="decimal.precision">
    <field name="name">Precio Kilogrado</field>
    <field name="digits">6</field>  <!-- Cambiado de 5 a 6 -->
</record>
```

**Después:**
1. Actualizar el módulo: `odoo-bin -u klo_account_invoice_uva`
2. Reiniciar el servidor de Odoo
3. Verificar en Configuración → Técnico → Base de Datos → Precisión Decimal

**Nota:** El campo `grado` usa precisión fija `digits=(16, 2)`. Para cambiarlo, modificar el modelo:

```python
# models/account_move_line.py
grado = fields.Float(string='Grado', digits=(16, 3))  # Cambiado a 3 decimales
```

---

### 9.4. Añadir Validaciones Personalizadas

**Ubicación:** `models/account_move_line.py`

**Ejemplo:** Validar que el grado esté entre 5 y 20:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    # ...campos existentes...
    
    @api.constrains('grado')
    def _check_grado_range(self):
        for line in self:
            if line.grado < 0:
                raise ValidationError('El grado no puede ser negativo.')
            if line.grado > 20:
                raise ValidationError('El grado no puede superar 20°.')
```

---

### 9.5. Aplicar la Vista de Uva a Otros Tipos de Facturas

**Actualmente:** Solo funciona con diarios de tipo 'sale' (Facturas de cliente).

**Para ampliar a Facturas de proveedor:**

1. **Modificar la vista del diario:**
   ```xml
   <!-- views/account_journal_views.xml -->
   <field name="es_para_uva"
          attrs="{'invisible': [('type', 'not in', ['sale', 'purchase'])]}"
          widget="boolean_toggle"/>
   ```

2. **Modificar el método de resolución del diario:**
   ```python
   # models/account_move.py
   @api.model
   def get_uva_formview_id_for_new(self):
       move_type = self._context.get('default_move_type', 'entry')
       # Añadir tipos de proveedor
       if move_type in ('out_invoice', 'out_refund', 'out_receipt'):
           journal_types = ['sale']
       elif move_type in ('in_invoice', 'in_refund', 'in_receipt'):
           journal_types = ['purchase']  # Ya estaba incluido
       else:
           return False
       # ...resto del código...
   ```

**No se requieren más cambios** porque la vista y el reporte ya funcionan con cualquier `account.move`.

---

### 9.6. Solución de Problemas Comunes

#### Problema: La vista de uva no se abre al crear facturas

**Diagnóstico:**
1. Verificar que el diario tiene `es_para_uva = True`
2. Comprobar en el navegador (Consola de desarrollador) si hay errores JS
3. Revisar los logs del servidor: `grep "get_uva_formview_id_for_new" odoo.log`

**Posible causa:** El parche JavaScript no se ha cargado.

**Solución:**
1. Limpiar caché del navegador
2. Actualizar assets: `odoo-bin --update=klo_account_invoice_uva --stop-after-init`
3. Reiniciar servidor y recargar la página con Ctrl+F5

---

#### Problema: Error "this._super is not a function" en JavaScript

**Causa:** No se guardó `this._super` antes del primer `await` en métodos async.

**Solución:** Revisar `static/src/js/account_move_list_open.js` y asegurar que todos los métodos async tienen:

```javascript
async methodName() {
    const superFn = this._super.bind(this);  // ✅ Primera línea
    
    await ...;
    
    return superFn();  // ✅ Usar superFn, no this._super
}
```

---

#### Problema: El PDF no usa el template de uva

**Diagnóstico:**
1. Abrir la factura y ejecutar en el shell de Python:
   ```python
   invoice = env['account.move'].browse(INVOICE_ID)
   print(invoice._get_name_invoice_report())
   # Debe devolver: 'klo_account_invoice_uva.klo_report_invoice_document_uva'
   ```

**Posibles causas:**
1. El diario no tiene `es_para_uva = True`
2. El método `_get_name_invoice_report()` no se ha cargado (actualizar módulo)
3. Los wrappers no se han registrado correctamente

**Solución:**
```bash
odoo-bin -u klo_account_invoice_uva --stop-after-init
```

---

#### Problema: Desalineación de columnas en el PDF

**Causa:** Diferente número de columnas `<th>` en cabeceras vs `<td>` en datos.

**Diagnóstico:**
Contar columnas en `report/report_invoice_uva.xml`:
- **Cabeceras (`<thead>`):** Deben ser exactamente 6 `<th>` visibles
- **Datos (`<tbody>`):** Deben ser exactamente 6 `<td>` por línea

**Solución actual (2026-04-14):**
El problema estaba en que se dejaban columnas vacías (`<th/>`) o ocultas (`display:none`) que seguían ocupando espacio. Se solucionó:
1. Eliminando completamente `th_priceunit`, `th_price_unit`, `th_taxes`
2. Reutilizando `th_subtotal` como columna "Importe"

Ver: `docs/fix_alineacion_importe.md` para más detalles.

---

## 10. Mantenimiento y Actualización

### 10.1. Actualizar el Módulo tras Modificaciones

**Comando básico:**
```bash
cd /ruta/a/odoo
./odoo-bin -c /ruta/a/config.conf -u klo_account_invoice_uva --stop-after-init
```

**Con base de datos específica:**
```bash
./odoo-bin -c config.conf -d nombre_bd -u klo_account_invoice_uva --stop-after-init
```

**Forzar recreación de vistas:**
```bash
./odoo-bin -c config.conf -d nombre_bd -u klo_account_invoice_uva --init=klo_account_invoice_uva --stop-after-init
```

---

### 10.2. Verificar Integridad del Módulo

**1. Verificar que los modelos se han cargado:**
```python
# Shell de Python
env['account.journal']._fields.get('es_para_uva')
# Debe devolver: <odoo.fields.Boolean ...>

env['account.move.line']._fields.get('precio_kilogrado')
# Debe devolver: <odoo.fields.Float ...>
```

**2. Verificar vistas registradas:**
```python
# Shell de Python
env.ref('klo_account_invoice_uva.view_move_form_uva')
# Debe devolver: ir.ui.view(ID)

env.ref('klo_account_invoice_uva.klo_report_invoice_document_uva')
# Debe devolver: ir.ui.view(ID)
```

**3. Verificar precisión decimal:**
```python
# Shell de Python
precision = env['decimal.precision'].search([('name', '=', 'Precio Kilogrado')])
print(precision.digits)
# Debe devolver: 5
```

---

### 10.3. Migración a Versiones Superiores de Odoo

**Cambios potenciales en Odoo 17+:**

1. **Sistema de assets:** Verificar que la sintaxis de `assets` en `__manifest__.py` sigue siendo compatible
2. **OWL Components:** El parche de `ListController` podría requerir adaptación si cambia la estructura de controladores
3. **QWeb reportes:** La estructura base de `report_invoice_document` podría cambiar
4. **API de precisión decimal:** Verificar que `decimal.precision` sigue siendo el mecanismo estándar

**Recomendación:** Probar el módulo en un entorno de desarrollo antes de migrar en producción.

---

## 11. Historial de Cambios Importantes

### 2026-04-14: Corrección de Alineación en Reporte PDF

**Problema:** La columna "Importe" en las líneas no estaba alineada con el total del pie.

**Causa:** Columnas vacías (`<th/>`) y ocultas (`display:none`) ocupaban espacio.

**Solución:**
- Eliminadas completamente las columnas `th_priceunit`, `th_price_unit` y `th_taxes`
- Reutilizada la columna `th_subtotal` cambiando solo su etiqueta a "Importe"
- Resultado: 6 columnas perfectamente alineadas

**Documentación:** Ver `docs/fix_alineacion_importe.md`

---

## 12. Referencias y Recursos

### Documentación de Odoo

- **Vistas:** https://www.odoo.com/documentation/16.0/developer/reference/backend/views.html
- **QWeb Reportes:** https://www.odoo.com/documentation/16.0/developer/reference/backend/reports.html
- **API JS (OWL):** https://www.odoo.com/documentation/16.0/developer/reference/frontend/javascript_reference.html
- **Patches JS:** https://www.odoo.com/documentation/16.0/developer/reference/frontend/patching_code.html

### Archivos Relacionados de Odoo Core

- `addons/account/models/account_move.py`
- `addons/account/views/account_move_views.xml`
- `addons/account/views/report_invoice.xml`
- `addons/web/static/src/views/list/list_controller.js`

---

## 13. Contacto y Soporte

**Autor:** Manuel Calomarde Gomez  
**Empresa:** KLO Ingenieria Informatica S.L.L.  
**GitHub:** klosll  
**Versión del Documento:** 1.0  
**Fecha:** 2026-04-14  

---

## 14. Licencia

Este módulo está licenciado bajo **LGPL-3** (GNU Lesser General Public License v3.0).

Puedes usar, modificar y distribuir este módulo libremente, siempre que mantengas la misma licencia en las modificaciones derivadas.

---

## 15. Notas para Futuras IAs

### Enfoque Recomendado al Modificar el Módulo

1. **Leer completamente este documento** antes de hacer cambios
2. **Entender el flujo completo** (sección 8) para saber dónde intervenir
3. **Modificar un componente a la vez** (modelo, vista o reporte)
4. **Actualizar el módulo** y verificar errores tras cada cambio
5. **Probar en navegador** y generar PDF para validar cambios visuales
6. **Actualizar esta documentación** si se añaden funcionalidades significativas

### Puntos Críticos a No Olvidar

- ✅ Al añadir campos a `account.move.line`, añadirlos también en la vista y en el reporte
- ✅ Al modificar fórmulas, actualizar **todos** los `@api.onchange` relacionados
- ✅ Al modificar el reporte PDF, asegurar que el número de `<th>` = número de `<td>`
- ✅ Al modificar JavaScript async, **siempre** guardar `this._super` antes del primer `await`
- ✅ Tras cambios en `data/`, usar `--init` en lugar de `-u` para forzar recreación de datos

### Estructura de Pensamiento Recomendada

```
¿Qué quiere hacer el usuario?
  ↓
¿Afecta a datos (modelos)?
  → Modificar models/*.py
  → Actualizar módulo con -u
  ↓
¿Afecta a la interfaz (vistas)?
  → Modificar views/*.xml
  → Actualizar módulo con -u
  ↓
¿Afecta al PDF (reportes)?
  → Modificar report/*.xml
  → Actualizar módulo con -u
  → Probar generación de PDF
  ↓
¿Afecta a comportamiento del cliente?
  → Modificar static/src/js/*.js
  → Actualizar assets
  → Limpiar caché del navegador
  ↓
Probar en entorno de desarrollo
  ↓
Documentar cambios en este archivo
```

---

**FIN DE LA DOCUMENTACIÓN TÉCNICA**

