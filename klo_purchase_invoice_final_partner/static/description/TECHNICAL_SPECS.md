# KLO Purchase and Invoice Final Partner - Especificaciones Técnicas
## Informacion General
| Campo | Valor |
|-------|-------|
| **Nombre del Modulo** | `klo_purchase_invoice_final_partner` |
| **Nombre Tecnico** | KLO Purchase and Invoice Final Partner |
| **Version** | 15.0.1.5.2 |
| **Categoria** | Purchase |
| **Licencia** | AGPL-3 |
| **Autor** | KLO Ingenieria Informatica S.L.L. |
| **Website** | https://www.klo.es |
| **Version de Odoo** | 15.0 |
## Objetivo del Modulo
Este modulo extiende la funcionalidad de compras y facturacion de Odoo 15 para permitir la asignacion de un **"Cliente de venta"** (sale_partner_id) en:
- Pedidos de compra (cabecera y lineas)
- Facturas de compra (cabecera y lineas)
- Lineas analiticas generadas desde facturas: el cliente de venta se asigna al campo estandar `partner_id` de `account.analytic.line`
El objetivo principal es poder rastrear **para que cliente final** se realizo una compra o gasto, facilitando la imputacion analitica y el seguimiento de costes por cliente.
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
### 2. Cliente de Venta en Facturas de Compra
#### Cabecera de la Factura (`account.move`)
- Aniade el campo `sale_partner_id` (Many2one a `res.partner`)
- Se hereda automaticamente desde el pedido de compra al facturar mediante `_prepare_invoice()`
- Visible en la vista formulario despues del campo "Referencia"
#### Lineas de la Factura (`account.move.line`)
- Aniade el campo `sale_partner_id` en cada linea
- **Prioridad de asignacion**:
  1. Si proviene de un pedido de compra: usa `purchase_line_id.sale_partner_id`
  2. Si no: usa `move_id.sale_partner_id` de la cabecera
- Es **editable** manualmente
- Visible en el arbol de lineas de factura despues de "Cuenta analitica"
**Comportamiento**:
```python
@api.depends('move_id.sale_partner_id', 'purchase_line_id.sale_partner_id')
def _compute_sale_partner_id(self):
    if not line._origin.sale_partner_id:
        # Prioridad: 1) linea del pedido, 2) cabecera factura
        if line.purchase_line_id and line.purchase_line_id.sale_partner_id:
            line.sale_partner_id = line.purchase_line_id.sale_partner_id
        else:
            line.sale_partner_id = line.move_id.sale_partner_id
```
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
            # KLO. El "Cliente de venta" se asigna como partner_id del apunte analitico
            result[i]['partner_id'] = move_line.sale_partner_id.id
    return result
```
**B) Lineas creadas por distribucion de etiquetas (via `_prepare_analytic_distribution_line`)**
```python
def _prepare_analytic_distribution_line(self, distribution):
    result = super()._prepare_analytic_distribution_line(distribution)
    if self.sale_partner_id:
        # KLO. El "Cliente de venta" se asigna como partner_id del apunte analitico
        result['partner_id'] = self.sale_partner_id.id
    return result
```
**C) Lineas creadas por templates analiticos del modulo AvanzOSC (`analytic_template_ids`)**
El modulo `account_analytic_distribution` (AvanzOSC) crea lineas analiticas adicionales en
su propio `action_post()` basandose en `account_id.analytic_template_ids`. Estas lineas quedan
vinculadas a la factura mediante `analytic_line_ids` (campo `account_move_id`).
Nuestro `action_post()` las gestiona despues del `super()`:
1. **Elimina** las que tengan `amount=0.0` y `move_id.balance != 0.0` (lineas inutiles generadas
   por templates con `percentage=0.0`)
2. **Propaga** `sale_partner_id` → `partner_id` en las que quedan validas
```python
def action_post(self):
    result = super().action_post()
    for move in self:
        # Eliminar lineas inutiles del template (amount=0 pero balance!=0)
        lines_to_delete = move.analytic_line_ids.filtered(
            lambda al: al.amount == 0.0 and al.move_id and al.move_id.balance != 0.0
        )
        if lines_to_delete:
            lines_to_delete.unlink()
        # Propagar partner_id en las lineas validas del template
        for analytic_line in move.analytic_line_ids:
            invoice_line = analytic_line.move_id
            if invoice_line and invoice_line.sale_partner_id and not analytic_line.partner_id:
                analytic_line.partner_id = invoice_line.sale_partner_id
    return result
```
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
          v                  | (3 mecanismos: analytic_account_id,
+-------------------------+  |  distribucion etiquetas, templates AvanzOSC)
|  Apuntes Analiticos     |  |
|  account.analytic.line  |  |
|  +-------------------+  |<-+
|  | partner_id        |  |  <- Campo ESTANDAR de Odoo
|  +-------------------+  |
+-------------------------+
```
## Arquitectura del Modulo
### Estructura de Archivos
```
klo_purchase_invoice_final_partner/
+-- __init__.py
+-- __manifest__.py
+-- models/
|   +-- __init__.py
|   +-- purchase.py              # PurchaseOrder, PurchaseOrderLine
|   +-- account_move.py          # AccountMove (action_post), AccountMoveLine
|   +-- account_analytic_line.py # Solo comentario explicativo (sin campos adicionales)
+-- views/
|   +-- purchase_view.xml        # Vistas de pedidos de compra
|   +-- account_move_view.xml    # Vistas de facturas
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
## Modelo de Datos
### Campos Aniadidos
#### `purchase.order`
```python
sale_partner_id = fields.Many2one(
    'res.partner',
    string='Cliente de venta',
    required=False
)
```
#### `purchase.order.line`
```python
sale_partner_id = fields.Many2one(
    'res.partner',
    string='Cliente de venta',
    compute='_compute_sale_partner_id',
    store=True,
    readonly=False,  # Permite edicion manual
)
```
#### `account.move`
```python
sale_partner_id = fields.Many2one(
    'res.partner',
    string='Cliente de venta',
    required=False
)
```
#### `account.move.line`
```python
sale_partner_id = fields.Many2one(
    'res.partner',
    string='Cliente de venta',
    compute='_compute_sale_partner_id',
    store=True,
    readonly=False,  # Permite edicion manual
)
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
## Metodos Principales Override
### 1. `purchase.order._prepare_invoice()`
**Proposito**: Propagar `sale_partner_id` de pedido a factura
```python
def _prepare_invoice(self):
    invoice_vals = super()._prepare_invoice()
    invoice_vals['sale_partner_id'] = self.sale_partner_id.id
    return invoice_vals
```
### 2. `purchase.order.line._prepare_account_move_line()`
**Proposito**: Propagar `sale_partner_id` y pre-computar `analytic_account_id` desde la cuenta contable del articulo
```python
def _prepare_account_move_line(self, move=False):
    result = super()._prepare_account_move_line(move=move)
    # 1. Propagar sale_partner_id
    if self.sale_partner_id:
        result['sale_partner_id'] = self.sale_partner_id.id
    # 2. Si no hay analitica, calcularla desde la cuenta contable de gasto del articulo
    if not result.get('analytic_account_id') and not self.display_type and self.product_id:
        accounts = self.product_id.product_tmpl_id.with_company(company).get_product_accounts(fiscal_pos=fiscal_pos)
        expense_account = accounts.get('expense') or move.journal_id.default_account_id
        if expense_account:
            rec = self.env['account.analytic.default'].account_get(
                product_id=self.product_id.id,
                partner_id=self.order_id.partner_id.id,
                account_id=expense_account.id,
                ...
            )
            if rec:
                result['analytic_account_id'] = rec.analytic_id.id
    return result
```
### 3. `account.move.line._compute_analytic_account_id()`
**Proposito**: Override con fallback a cuenta por defecto del diario cuando la logica estandar no encuentra regla
```python
@api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.journal_id')
def _compute_analytic_account_id(self):
    # Paso 1: Logica estandar de Odoo (via account.analytic.default)
    super()._compute_analytic_account_id()
    # Paso 2: Fallback - si aun no hay cuenta analitica, buscar por cuenta del diario
    for record in self:
        if not record.analytic_account_id:
            rec = self.env['account.analytic.default'].account_get(
                product_id=record.product_id.id,
                account_id=record.move_id.journal_id.default_account_id.id,
                ...
            )
            if rec:
                record.analytic_account_id = rec.analytic_id
```
### 4. `account.move.line._prepare_analytic_line()`
**Proposito**: Propagar `sale_partner_id` como `partner_id` en lineas analiticas creadas por `analytic_account_id`
```python
def _prepare_analytic_line(self):
    result = super()._prepare_analytic_line()
    for i, move_line in enumerate(self):
        if move_line.sale_partner_id and i < len(result):
            result[i]['partner_id'] = move_line.sale_partner_id.id  # KLO. -> partner_id
    return result
```
### 5. `account.move.line._prepare_analytic_distribution_line()`
**Proposito**: Propagar `sale_partner_id` como `partner_id` en lineas analiticas creadas por distribucion de etiquetas
```python
def _prepare_analytic_distribution_line(self, distribution):
    result = super()._prepare_analytic_distribution_line(distribution)
    if self.sale_partner_id:
        result['partner_id'] = self.sale_partner_id.id  # KLO. -> partner_id
    return result
```
### 6. `account.move.action_post()` *(nuevo en v15.0.1.5.1 / v15.0.1.5.2)*
**Proposito**: Gestionar las lineas analiticas creadas por el modulo `account_analytic_distribution`
(AvanzOSC) que se generan via `account_id.analytic_template_ids` en su propio `action_post()`.
Estas lineas quedan en `analytic_line_ids` (campo `account_move_id = factura.id`).
```python
def action_post(self):
    result = super().action_post()
    for move in self:
        # KLO. Eliminar lineas del template con amount=0 cuando la linea de factura tiene balance!=0
        # Causa: templates con percentage=0.0 generan lineas sin valor economico
        lines_to_delete = move.analytic_line_ids.filtered(
            lambda al: al.amount == 0.0 and al.move_id and al.move_id.balance != 0.0
        )
        if lines_to_delete:
            lines_to_delete.unlink()
        # KLO. Propagar partner_id desde sale_partner_id en las lineas validas del template
        for analytic_line in move.analytic_line_ids:
            invoice_line = analytic_line.move_id
            if invoice_line and invoice_line.sale_partner_id and not analytic_line.partner_id:
                analytic_line.partner_id = invoice_line.sale_partner_id
    return result
```
**Por que el filtro `amount=0 AND balance!=0` es seguro**:
- Si `percentage > 0` y `balance = 0.01` (minimo real), el amount es `0.01 * p / 100 > 0` -> no se elimina
- Solo puede ocurrir `amount=0 AND balance!=0` cuando `percentage=0.0` (verificado sobre todos los datos historicos)
- Las lineas legitimas con `balance=0` (articulos gratuitos, etc.) nunca se eliminan
## Comportamiento del Modulo `account_analytic_distribution` (AvanzOSC)
Este modulo (portado de v14) crea lineas analiticas adicionales al validar cualquier factura,
basandose en `analytic_template_ids` configurados en cada cuenta contable:
```python
# Codigo de AvanzOSC (account_analytic_distribution/models/account_move.py)
def action_post(self):
    result = super().action_post()
    for line in self.invoice_line_ids:
        if line.account_id and line.account_id.analytic_template_ids:
            for template in line.account_id.analytic_template_ids:
                analytic = self.env["account.analytic.line"].create({
                    "name": line.name,
                    "account_id": template.account_analytic_id.id,
                    "move_id": line.id})
                if template.percentage:  # False si percentage=0.0
                    if line.credit:
                        analytic.amount = (template.percentage * line.credit) / 100
                    if line.debit:
                        analytic.amount = (-1) * template.percentage * line.debit / 100
    return result
```
Las lineas se identifican por tener `account_move_id != NULL` (campo de la relacion
`analytic_line_ids` en `account.move`).
> **Recomendacion de configuracion**: Los 4 templates activos tienen `percentage=0.0`.
> Deberian configurarse con el porcentaje correcto (normalmente 100%) desde
> `Contabilidad > Configuracion > Plantillas analiticas`.
## Interfaces de Usuario
### Vistas Implementadas
#### 1. Pedidos de Compra
**Vista Arbol** (`purchase.purchase_order_kpis_tree`):
- Campo `sale_partner_id` despues de `partner_id`
- Opcional (oculto por defecto)
**Vista Formulario Cabecera** (`purchase.purchase_order_form`):
- Campo `sale_partner_id` despues de `partner_ref`
**Vista Formulario Lineas** (`purchase.purchase_order_form`):
- Campo `sale_partner_id` en el arbol de lineas despues de `account_analytic_id`
- Opcional (oculto por defecto)
#### 2. Facturas de Compra
**Vista Formulario Cabecera** (`account.view_move_form`):
- Campo `sale_partner_id` despues de `ref`
**Vista Formulario Lineas** (`account.view_move_form`):
- Campo `sale_partner_id` en el arbol de lineas despues de `analytic_account_id`
- Opcional (oculto por defecto)
#### 3. Apuntes Analiticos
> **v15.0.1.5.0**: Se eliminaron todas las vistas heredadas que mostraban `sale_partner_id`
> en apuntes analiticos y distribucion analitica. El campo `partner_id` estandar de Odoo
> ya es visible de forma nativa en todas las vistas de `account.analytic.line`.
## Casos de Uso
### Caso 1: Compra para Cliente Especifico
**Escenario**: Se compra material para un proyecto de un cliente especifico.
**Flujo**:
1. Crear pedido de compra
2. Asignar "Cliente de venta" en la cabecera
3. Las lineas heredan automaticamente el cliente
4. Al facturar, el cliente se propaga a la factura
5. Al validar la factura, `partner_id` de los apuntes analiticos = cliente de venta
**Resultado**: Todos los costes quedan asociados al cliente final.
### Caso 2: Compra Multi-Cliente
**Escenario**: Un pedido incluye productos para diferentes clientes.
**Flujo**:
1. Crear pedido de compra
2. Asignar diferentes "Clientes de venta" en cada linea
3. Al facturar, cada linea de factura mantiene su cliente
4. Los apuntes analiticos reflejan el cliente correcto por linea
**Resultado**: Reparto preciso de costes por cliente.
### Caso 3: Modificacion Manual
**Escenario**: Se necesita cambiar el cliente despues de crear el pedido/factura.
**Flujo**:
1. Editar el campo `sale_partner_id` en lineas
2. Los cambios se respetan (campo no es readonly)
3. Al validar la factura, se propaga el valor actualizado
**Resultado**: Flexibilidad para ajustes manuales.
## Consideraciones Tecnicas
### Campos Computados con Store
Los campos `sale_partner_id` en lineas usan:
- `compute='_compute_sale_partner_id'`
- `store=True` - Persiste en BD para busquedas
- `readonly=False` - Permite edicion manual
**Ventajas**:
- Auto-completado desde la cabecera
- Editables manualmente
- Consultables en filtros y agrupaciones
### Propagacion en Cascada
```
Pedido (sale_partner_id) -> Factura (sale_partner_id) -> Analitica (partner_id)
```
**Importante**:
- La propagacion ocurre en la **creacion** de registros
- Modificaciones posteriores NO se propagan automaticamente
- Esto es intencional para mantener trazabilidad
### Tres Mecanismos de Creacion de Lineas Analiticas
| Mecanismo | Metodo | Cuando | Partner propagado |
|-----------|--------|--------|------------------|
| Cuenta analitica directa | `_prepare_analytic_line()` | Al validar, si `analytic_account_id` | Si |
| Distribucion por etiquetas | `_prepare_analytic_distribution_line()` | Al validar, si `analytic_distribution` | Si |
| Templates AvanzOSC | `action_post()` de AvanzOSC + nuestro post-proceso | Al validar, si `account_id.analytic_template_ids` | Si (en post-proceso) |
### Asignacion Automatica de Cuenta Analitica (`analytic_account_id`)
> **Funcionalidad aniadida en v15.0.1.4.0**
#### Cadena de Prioridad Implementada
```
1. Tiene el pedido account_analytic_id en la linea? -> Usar ese valor (comportamiento estandar)
      |
      v No
2. Hay regla en account.analytic.default para la cuenta contable de gasto del articulo?
   (product_id + cuenta gasto de get_product_accounts() + date + company)
      | Si -> Asignar analytic_id de esa regla
      |
      v No
3. Hay regla en account.analytic.default para la cuenta por defecto del diario?
   (product_id + journal.default_account_id + date + company)
      | Si -> Asignar analytic_id de esa regla
      |
      v No
4. Sin cuenta analitica (campo vacio)
```
#### Implementacion en Dos Capas
| Capa | Metodo | Momento |
|------|--------|---------|
| 1a | `purchase.order.line._prepare_account_move_line()` | Al crear la linea de factura desde el pedido |
| 2a | `account.move.line._compute_analytic_account_id()` | Al calcular el campo computado (store) |
## Testing y Validacion
### Pruebas Recomendadas
1. **Test de Propagacion Basica**:
   - Crear pedido con cliente -> verificar heredado en lineas
   - Facturar -> verificar en factura
   - Validar -> verificar `partner_id` en apuntes analiticos = cliente de venta
2. **Test de Edicion Manual**:
   - Cambiar cliente en linea de pedido
   - Verificar que se mantiene en factura y en analitica
3. **Test Multi-Cliente**:
   - Pedido con diferentes clientes por linea
   - Verificar correcta separacion en analitica
4. **Test de Distribucion Analitica**:
   - Usar etiquetas analiticas
   - Verificar que `partner_id` de las lineas analiticas = cliente de venta
5. **Test de Templates AvanzOSC**:
   - Factura con cuenta contable que tiene `analytic_template_ids` con `percentage > 0`
   - Validar: lineas del template deben tener `partner_id` = cliente de venta y `amount != 0`
   - Factura con template de `percentage=0`: verificar que NO se crean lineas analiticas inutiles
6. **Test de Cuenta Analitica Automatica** (v15.0.1.4.0):
   - Crear pedido sin cuenta analitica manual
   - Crear factura desde el pedido
   - Verificar que `analytic_account_id` se asigna automaticamente en las lineas de factura
## Seguridad y Permisos
El modulo **NO aniade** nuevos grupos ni reglas de acceso especificas. Utiliza los permisos estandar de:
- `purchase.group_purchase_user`
- `account.group_account_invoice`
- `analytic.group_analytic_accounting`
## Instalacion y Configuracion
### Requisitos Previos
- Odoo 15.0
- Modulos base: `purchase_stock`, `account`, `analytic`, `account_analytic_distribution`
### Pasos de Instalacion
1. Copiar modulo a `addons` o `extra-addons`
2. Actualizar lista de aplicaciones
3. Instalar "KLO Purchase and Invoice Final Partner"
4. No requiere configuracion adicional
### Post-Instalacion
- Los campos aparecen automaticamente en las vistas
- No se necesitan datos de demostracion
- Compatible con datos existentes (no migra datos anteriores)
## Troubleshooting
### Problema: El campo no aparece en la vista
**Solucion**: Verificar que las vistas heredadas existen (depende de modulos base).
### Problema: El cliente no se propaga a analitica
**Solucion**: Verificar que la factura se valida correctamente (`action_post`).
### Problema: No puedo editar el campo en la linea
**Solucion**: El campo solo se auto-completa en nuevas lineas. Verificar `readonly=False`.
### Problema: `analytic_account_id` vacio en lineas de factura de compra
**Causa**: El pedido de compra no tenia cuenta analitica asignada manualmente.
**Solucion** (v15.0.1.4.0): El override de `_prepare_account_move_line()` pre-computa la cuenta
analitica usando `get_product_accounts()`. El override de `_compute_analytic_account_id()` incluye
fallback al diario. Con ambas capas la cuenta se asigna automaticamente.
### Problema: Se crean lineas analiticas duplicadas con `amount=0`
**Causa**: El modulo `account_analytic_distribution` (AvanzOSC) crea lineas adicionales desde
`analytic_template_ids` de la cuenta contable. Si el template tiene `percentage=0.0`, el codigo
de AvanzOSC (`if template.percentage:` -> False) nunca calcula el importe y lo deja en 0.
**Solucion** (v15.0.1.5.2): El override de `action_post()` elimina automaticamente estas lineas
cuando `amount=0` y la linea de factura tiene `balance!=0`.
**Solucion definitiva**: Configurar `percentage=100` en los templates desde
`Contabilidad > Configuracion > Plantillas analiticas`.
### Problema: `partner_id` vacio en apuntes analiticos creados por templates AvanzOSC
**Causa**: El modulo AvanzOSC no conoce `sale_partner_id` y no asigna `partner_id`.
**Solucion** (v15.0.1.5.1): El override de `action_post()` propaga `sale_partner_id` -> `partner_id`
despues del `super()` en las lineas de `analytic_line_ids`.
## Changelog
### Version 15.0.1.5.2 (2026-04-22)
- Eliminacion automatica en `action_post()` de lineas analiticas de templates con `amount=0`
  cuando la linea de factura tiene `balance!=0` (generadas por templates con `percentage=0.0`)
- Filtro seguro: verificado que no puede eliminar lineas validas con `percentage > 0` en ningun
  escenario real (balance minimo 0.01 EUR, amount resultante siempre > 0 si percentage > 0)
### Version 15.0.1.5.1 (2026-04-22)
- Aniadido override de `AccountMove.action_post()` para propagar `sale_partner_id` -> `partner_id`
  en las lineas analiticas creadas por el modulo AvanzOSC via `analytic_template_ids`
  (accesibles mediante `analytic_line_ids`, campo `account_move_id`)
### Version 15.0.1.5.0 (2026-04-22)
- Eliminado campo `sale_partner_id` de `account.analytic.line`
- El valor de `sale_partner_id` de `account.move.line` se propaga ahora al campo estandar
  `partner_id` de `account.analytic.line` al validar la factura de compra
- Metodos `_prepare_analytic_line()` y `_prepare_analytic_distribution_line()` actualizados
  para asignar `partner_id` en lugar de `sale_partner_id`
- Eliminadas todas las vistas heredadas de `sale_partner_id` en apuntes analiticos
### Version 15.0.1.4.0 (2026-04-10)
- Fix: `analytic_account_id` ahora se asigna correctamente en lineas de factura creadas
  desde pedidos de compra
- Override de `purchase.order.line._prepare_account_move_line()` con pre-computo de
  `analytic_account_id` usando `get_product_accounts()` + `account.analytic.default.account_get()`
- Override de `account.move.line._compute_analytic_account_id()` con fallback a
  `journal_id.default_account_id` cuando la logica estandar no halla regla
- `@api.depends` ampliado con `move_id.journal_id` para recomputo correcto al cambiar el diario
### Version 15.0.1.3.0 (2025-04-10)
- Aniadido campo `sale_partner_id` en lineas de pedido de compra
- Aniadido campo `sale_partner_id` en lineas de factura de compra
- Propagacion desde linea de pedido a linea de factura
- Prioridad de asignacion: pedido > cabecera factura
### Version 15.0.1.2.0 (Anterior)
- Aniadida propagacion a lineas analiticas con distribucion
- Mejoras en vistas de apuntes analiticos
### Version 15.0.1.1.0 (Inicial)
- Implementacion base del campo `sale_partner_id`
- Propagacion desde pedido a factura a analitica
## Contribuidores
- **KLO Ingenieria Informatica S.L.L.** - Desarrollo y mantenimiento
- Basado en concepto original de Ecosoft Co., Ltd (2019)
## Soporte
**Contacto**: KLO Ingenieria Informatica S.L.L.
**Website**: https://www.klo.es
**Version del documento**: 2.0
**Fecha**: 2026-04-22
---
**Nota**: Este documento forma parte de la documentacion tecnica interna de KLO para modulos de Odoo 15.
