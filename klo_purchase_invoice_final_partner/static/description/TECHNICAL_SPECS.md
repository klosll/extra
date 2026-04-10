# KLO Purchase and Invoice Final Partner - Especificaciones Técnicas

## 📋 Información General

| Campo | Valor |
|-------|-------|
| **Nombre del Módulo** | `klo_purchase_invoice_final_partner` |
| **Nombre Técnico** | KLO Purchase and Invoice Final Partner |
| **Versión** | 15.0.1.4.0 |
| **Categoría** | Purchase |
| **Licencia** | AGPL-3 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Website** | https://www.klo.es |
| **Versión de Odoo** | 15.0 |

## 🎯 Objetivo del Módulo

Este módulo extiende la funcionalidad de compras y facturación de Odoo 15 para permitir la asignación de un **"Cliente de venta"** (sale_partner_id) en:

- Pedidos de compra (cabecera y líneas)
- Facturas de compra (cabecera y líneas)
- Líneas analíticas generadas desde facturas

El objetivo principal es poder rastrear **para qué cliente final** se realizó una compra o gasto, facilitando la imputación analítica y el seguimiento de costes por cliente.

## 🔧 Funcionalidades Principales

### 1. Cliente de Venta en Pedidos de Compra

#### Cabecera del Pedido (`purchase.order`)
- Añade el campo `sale_partner_id` (Many2one a `res.partner`)
- Permite indicar el cliente final para el que se realiza la compra
- Visible en la vista formulario después del campo "Referencia del proveedor"
- Opcional en la vista árbol (columna oculta por defecto)

#### Líneas del Pedido (`purchase.order.line`)
- Añade el campo `sale_partner_id` en cada línea
- Se auto-completa desde la cabecera del pedido mediante `@api.depends`
- Es **editable** por línea, permitiendo diferentes clientes por producto
- Visible en el árbol de líneas después de "Cuenta analítica"

**Comportamiento**:
```python
@api.depends('order_id.sale_partner_id')
def _compute_sale_partner_id(self):
    # Solo asigna si la línea aún no tiene valor propio guardado
    if not line._origin.sale_partner_id:
        line.sale_partner_id = line.order_id.sale_partner_id
```

### 2. Cliente de Venta en Facturas de Compra

#### Cabecera de la Factura (`account.move`)
- Añade el campo `sale_partner_id` (Many2one a `res.partner`)
- Se hereda automáticamente desde el pedido de compra al facturar mediante `_prepare_invoice()`
- Visible en la vista formulario después del campo "Referencia"

#### Líneas de la Factura (`account.move.line`)
- Añade el campo `sale_partner_id` en cada línea
- **Prioridad de asignación**:
  1. Si proviene de un pedido de compra → usa `purchase_line_id.sale_partner_id`
  2. Si no → usa `move_id.sale_partner_id` de la cabecera
- Es **editable** manualmente
- Visible en el árbol de líneas de factura después de "Cuenta analítica"

**Comportamiento**:
```python
@api.depends('move_id.sale_partner_id', 'purchase_line_id.sale_partner_id')
def _compute_sale_partner_id(self):
    if not line._origin.sale_partner_id:
        # Prioridad: 1) línea del pedido, 2) cabecera factura
        if line.purchase_line_id and line.purchase_line_id.sale_partner_id:
            line.sale_partner_id = line.purchase_line_id.sale_partner_id
        else:
            line.sale_partner_id = line.move_id.sale_partner_id
```

### 3. Propagación a Líneas Analíticas

#### Apuntes Analíticos (`account.analytic.line`)
- Añade el campo `sale_partner_id` (Many2one a `res.partner`, indexado)
- Se propaga **automáticamente** desde la línea de factura al validar (action_post)
- Compatible con:
  - Asignación directa de cuenta analítica (`analytic_account_id`)
  - Distribución analítica por etiquetas (`analytic_distribution`)

**Métodos de propagación**:
```python
# Para cuenta analítica directa
def _prepare_analytic_line(self):
    result = super()._prepare_analytic_line()
    if move_line.sale_partner_id:
        result[i]['sale_partner_id'] = move_line.sale_partner_id.id

# Para distribución por etiquetas
def _prepare_analytic_distribution_line(self, distribution):
    result = super()._prepare_analytic_distribution_line(distribution)
    if self.sale_partner_id:
        result['sale_partner_id'] = self.sale_partner_id.id
```

## 📊 Flujo de Datos

```
┌─────────────────────────┐
│  Pedido de Compra       │
│  purchase.order         │
│  ┌───────────────────┐  │
│  │ sale_partner_id   │──┼──┐
│  └───────────────────┘  │  │
│          │              │  │
│          ▼              │  │
│  ┌───────────────────┐  │  │
│  │ Líneas del Pedido │  │  │
│  │ sale_partner_id   │  │  │
│  └───────────────────┘  │  │
└─────────────────────────┘  │
          │                  │
          │ Facturar         │ _prepare_invoice()
          ▼                  │
┌─────────────────────────┐  │
│  Factura de Compra      │  │
│  account.move           │  │
│  ┌───────────────────┐  │◄─┘
│  │ sale_partner_id   │  │
│  └───────────────────┘  │
│          │              │
│          ▼              │
│  ┌───────────────────┐  │
│  │ Líneas Factura    │  │
│  │ sale_partner_id   │──┼──┐
│  └───────────────────┘  │  │
└─────────────────────────┘  │
          │                  │ Validar factura
          │ action_post()    │ (action_post)
          ▼                  │
┌─────────────────────────┐  │
│  Apuntes Analíticos     │  │
│  account.analytic.line  │  │
│  ┌───────────────────┐  │◄─┘
│  │ sale_partner_id   │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

## 🏗️ Arquitectura del Módulo

### Estructura de Archivos

```
klo_purchase_invoice_final_partner/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── purchase.py              # PurchaseOrder, PurchaseOrderLine
│   ├── account_move.py          # AccountMove, AccountMoveLine
│   └── account_analytic_line.py # AccountAnalyticLine
├── views/
│   ├── purchase_view.xml        # Vistas de pedidos de compra
│   ├── account_move_view.xml    # Vistas de facturas
│   └── account_analytic_line_view.xml  # Vistas de analítica
└── static/
    └── description/
        ├── icon.png
        └── TECHNICAL_SPECS.md   # Este archivo
```

### Dependencias del Módulo

```python
"depends": [
    "purchase_stock",           # Gestión de compras con inventario
    "account",                  # Módulo de contabilidad
    "analytic",                 # Cuentas analíticas
    "account_analytic_distribution",  # Distribución analítica por etiquetas
]
```

## 💾 Modelo de Datos

### Campos Añadidos

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
    readonly=False,  # Permite edición manual
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
    readonly=False,  # Permite edición manual
)
```

#### `account.analytic.line`
```python
sale_partner_id = fields.Many2one(
    'res.partner',
    string='Cliente de venta',
    index=True,  # Indexado para búsquedas rápidas
)
```

### Relaciones entre Modelos

```
res.partner ←── Many2one ─── purchase.order.sale_partner_id
res.partner ←── Many2one ─── purchase.order.line.sale_partner_id
res.partner ←── Many2one ─── account.move.sale_partner_id
res.partner ←── Many2one ─── account.move.line.sale_partner_id
res.partner ←── Many2one ─── account.analytic.line.sale_partner_id
```

## 🔄 Métodos Principales Override

### 1. `purchase.order._prepare_invoice()`
**Propósito**: Propagar `sale_partner_id` de pedido a factura

```python
def _prepare_invoice(self):
    invoice_vals = super()._prepare_invoice()
    invoice_vals['sale_partner_id'] = self.sale_partner_id.id
    return invoice_vals
```

### 2. `purchase.order.line._prepare_account_move_line()`
**Propósito**: Propagar `sale_partner_id` y pre-computar `analytic_account_id` desde la cuenta contable del artículo

```python
def _prepare_account_move_line(self, move=False):
    result = super()._prepare_account_move_line(move=move)
    # 1. Propagar sale_partner_id
    if self.sale_partner_id:
        result['sale_partner_id'] = self.sale_partner_id.id
    # 2. Si no hay analítica, calcularla desde la cuenta contable de gasto del artículo
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
**Propósito**: Override con fallback a cuenta por defecto del diario cuando la lógica estándar no encuentra regla

```python
@api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.journal_id')
def _compute_analytic_account_id(self):
    # Paso 1: Lógica estándar de Odoo (via account.analytic.default con account_id del artículo)
    super()._compute_analytic_account_id()
    # Paso 2: Fallback - si aún no hay cuenta analítica, buscar por cuenta del diario
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
**Propósito**: Propagar `sale_partner_id` a líneas analíticas (cuenta analítica directa)

```python
def _prepare_analytic_line(self):
    result = super()._prepare_analytic_line()
    for i, move_line in enumerate(self):
        if move_line.sale_partner_id and i < len(result):
            result[i]['sale_partner_id'] = move_line.sale_partner_id.id
    return result
```

### 5. `account.move.line._prepare_analytic_distribution_line()`
**Propósito**: Propagar `sale_partner_id` a líneas analíticas (distribución por etiquetas)

```python
def _prepare_analytic_distribution_line(self, distribution):
    result = super()._prepare_analytic_distribution_line(distribution)
    if self.sale_partner_id:
        result['sale_partner_id'] = self.sale_partner_id.id
    return result
```

## 🖥️ Interfaces de Usuario

### Vistas Implementadas

#### 1. Pedidos de Compra

**Vista Árbol** (`purchase.purchase_order_kpis_tree`):
- Campo `sale_partner_id` después de `partner_id`
- Opcional (oculto por defecto)

**Vista Formulario Cabecera** (`purchase.purchase_order_form`):
- Campo `sale_partner_id` después de `partner_ref`

**Vista Formulario Líneas** (`purchase.purchase_order_form`):
- Campo `sale_partner_id` en el árbol de líneas después de `account_analytic_id`
- Opcional (oculto por defecto)

#### 2. Facturas de Compra

**Vista Formulario Cabecera** (`account.view_move_form`):
- Campo `sale_partner_id` después de `ref`

**Vista Formulario Líneas** (`account.view_move_form`):
- Campo `sale_partner_id` en el árbol de líneas después de `analytic_account_id`
- Opcional (oculto por defecto)

#### 3. Apuntes Analíticos

**Vista Formulario** (`account.view_account_analytic_line_form_inherit_account`):
- Campo `sale_partner_id` después de `partner_id`

**Vista Árbol** (`account.view_account_analytic_line_tree_inherit_account`):
- Campo `sale_partner_id` después de `partner_id`
- Opcional (oculto por defecto)

**Vista Distribución Analítica** (`account_analytic_distribution.account_move_line_distribution_form_view`):
- Campo `sale_partner_id` en el árbol de líneas analíticas después de `account_id`
- Visible por defecto

## 📈 Casos de Uso

### Caso 1: Compra para Cliente Específico

**Escenario**: Se compra material para un proyecto de un cliente específico.

**Flujo**:
1. Crear pedido de compra
2. Asignar "Cliente de venta" en la cabecera
3. Las líneas heredan automáticamente el cliente
4. Al facturar, el cliente se propaga a la factura
5. Al validar la factura, las líneas analíticas incluyen el cliente

**Resultado**: Todos los costes quedan asociados al cliente final.

### Caso 2: Compra Multi-Cliente

**Escenario**: Un pedido incluye productos para diferentes clientes.

**Flujo**:
1. Crear pedido de compra
2. Asignar diferentes "Clientes de venta" en cada línea
3. Al facturar, cada línea de factura mantiene su cliente
4. Las líneas analíticas reflejan el cliente correcto por línea

**Resultado**: Reparto preciso de costes por cliente.

### Caso 3: Modificación Manual

**Escenario**: Se necesita cambiar el cliente después de crear el pedido/factura.

**Flujo**:
1. Editar el campo `sale_partner_id` en líneas
2. Los cambios se respetan (campo no es readonly)
3. Al validar la factura, se propaga el valor actualizado

**Resultado**: Flexibilidad para ajustes manuales.

## 🔍 Consideraciones Técnicas

### Campos Computados con Store

Los campos `sale_partner_id` en líneas usan:
- `compute='_compute_sale_partner_id'`
- `store=True` - Persiste en BD para búsquedas
- `readonly=False` - Permite edición manual

**Ventajas**:
- Auto-completado desde la cabecera
- Editables manualmente
- Consultables en filtros y agrupaciones
- No recalculan en cada lectura

### Propagación en Cascada

El flujo de propagación es:
```
Pedido → Factura → Líneas Analíticas
```

**Importante**: 
- La propagación ocurre en la **creación** de registros
- Modificaciones posteriores NO se propagan automáticamente
- Esto es intencional para mantener trazabilidad

### Compatibilidad con Distribución Analítica

El módulo es compatible con **dos sistemas de analítica**:

1. **Cuenta analítica directa** (`analytic_account_id`):
   - Propagación vía `_prepare_analytic_line()`

2. **Distribución por etiquetas** (`analytic_distribution`):
   - Propagación vía `_prepare_analytic_distribution_line()`

Ambos métodos propagan correctamente `sale_partner_id`.

### Asignación Automática de Cuenta Analítica (`analytic_account_id`)

> **Funcionalidad añadida en v15.0.1.4.0**

#### Problema Resuelto

Antes de esta versión, al crear una factura desde un pedido de compra, el campo `analytic_account_id` en las líneas de factura podía quedar vacío si el pedido de compra no tenía cuenta analítica asignada manualmente. Esto ocurría porque:

1. `purchase.order.line._compute_account_analytic_id()` busca reglas analíticas usando solo `product_id` y `partner_id` del proveedor (sin la cuenta contable de gasto del artículo). Al no coincidir con ninguna regla de `account.analytic.default`, deja `account_analytic_id = False` en la línea.
2. `_prepare_account_move_line()` propaga ese `False` a la línea de factura.
3. El campo `analytic_account_id` en `account.move.line` es `store=True`, por lo que el valor `False` queda guardado sin reasignarse.

#### Cadena de Prioridad Implementada

```
1. ¿Tiene el pedido account_analytic_id en la línea? → Usar ese valor (comportamiento estándar)
      │
      ▼ No
2. ¿Hay regla en account.analytic.default para la cuenta contable de gasto del artículo?
   (product_id + cuenta gasto de get_product_accounts() + date + company)
      │ Sí → Asignar analytic_id de esa regla
      │
      ▼ No
3. ¿Hay regla en account.analytic.default para la cuenta por defecto del diario?
   (product_id + journal.default_account_id + date + company)
      │ Sí → Asignar analytic_id de esa regla
      │
      ▼ No
4. Sin cuenta analítica (campo vacío)
```

#### Implementación en Dos Capas

| Capa | Método | Momento |
|------|--------|---------|
| 1ª | `purchase.order.line._prepare_account_move_line()` | Al crear la línea de factura desde el pedido |
| 2ª | `account.move.line._compute_analytic_account_id()` | Al calcular el campo computado (store) |

La primera capa garantiza que el valor correcto se pase en el diccionario `create`. La segunda actúa como red de seguridad para líneas creadas por otros caminos (por ejemplo, facturas manuales de compra).

### Índices de Base de Datos

Campo indexado:
- `account.analytic.line.sale_partner_id` - Para filtrado rápido

## 🧪 Testing y Validación

### Pruebas Recomendadas

1. **Test de Propagación Básica**:
   - Crear pedido con cliente → verificar heredado en líneas
   - Facturar → verificar en factura
   - Validar → verificar en analítica

2. **Test de Edición Manual**:
   - Cambiar cliente en línea de pedido
   - Verificar que se mantiene en factura

3. **Test Multi-Cliente**:
   - Pedido con diferentes clientes por línea
   - Verificar correcta separación en analítica

4. **Test de Distribución Analítica**:
   - Usar etiquetas analíticas
   - Verificar propagación del cliente

5. **Test de Vista Distribución**:
   - Abrir distribución analítica desde línea de factura
   - Verificar que `sale_partner_id` es visible

6. **Test de Cuenta Analítica Automática** (v15.0.1.4.0):
   - Crear pedido de compra con artículos cuya categoría tenga cuenta contable de gasto configurada
   - NO asignar cuenta analítica manualmente en el pedido
   - Crear factura desde el pedido
   - Verificar que `analytic_account_id` se asigna automáticamente en las líneas de factura
   - Validar que coincide con la regla de `account.analytic.default` para esa cuenta contable

## 🔒 Seguridad y Permisos

El módulo **NO añade** nuevos grupos ni reglas de acceso específicas. Utiliza los permisos estándar de:
- `purchase.group_purchase_user`
- `account.group_account_invoice`
- `analytic.group_analytic_accounting`

## 🚀 Instalación y Configuración

### Requisitos Previos

- Odoo 15.0
- Módulos base: `purchase_stock`, `account`, `analytic`, `account_analytic_distribution`

### Pasos de Instalación

1. Copiar módulo a `addons` o `extra-addons`
2. Actualizar lista de aplicaciones
3. Instalar "KLO Purchase and Invoice Final Partner"
4. No requiere configuración adicional

### Post-Instalación

- Los campos aparecen automáticamente en las vistas
- No se necesitan datos de demostración
- Compatible con datos existentes (no migra datos anteriores)

## 🐛 Troubleshooting

### Problema: El campo no aparece en la vista

**Solución**: Verificar que las vistas heredadas existen (depende de módulos base).

### Problema: El cliente no se propaga a analítica

**Solución**: Verificar que la factura se valida correctamente (action_post).

### Problema: No puedo editar el campo en la línea

**Solución**: El campo solo se auto-completa en nuevas líneas. Verificar `readonly=False`.

### Problema: `analytic_account_id` vacío en líneas de factura de compra

**Causa**: El pedido de compra no tenía cuenta analítica asignada manualmente, y la lógica estándar de `_compute_account_analytic_id` en `purchase.order.line` no usa la cuenta contable de gasto del artículo (solo `product_id` y `partner_id` del proveedor), por lo que no encuentra la regla de `account.analytic.default`.

**Solución** (v15.0.1.4.0): El override de `_prepare_account_move_line()` en `PurchaseOrderLine` ahora pre-computa la cuenta analítica usando la cuenta contable de gasto del artículo (vía `get_product_accounts()`). Adicionalmente, `_compute_analytic_account_id()` en `AccountMoveLine` incluye un fallback a la cuenta por defecto del diario. Con ambas capas, la cuenta analítica se asigna correctamente sin necesidad de intervención manual.

## 📝 Changelog

### Versión 15.0.1.4.0 (2026-04-10)
- ✅ **Fix**: `analytic_account_id` ahora se asigna correctamente en líneas de factura creadas desde pedidos de compra
- ✅ Override de `purchase.order.line._prepare_account_move_line()` con pre-cómputo de `analytic_account_id` usando `get_product_accounts()` + `account.analytic.default.account_get()`
- ✅ Override de `account.move.line._compute_analytic_account_id()` con fallback a `journal_id.default_account_id` cuando la lógica estándar no halla regla
- ✅ `@api.depends` ampliado con `move_id.journal_id` para recomputo correcto al cambiar el diario

### Versión 15.0.1.3.0 (2025-04-10)
- ✅ Añadido campo `sale_partner_id` en líneas de pedido de compra
- ✅ Añadido campo `sale_partner_id` en líneas de factura de compra
- ✅ Propagación desde línea de pedido a línea de factura
- ✅ Vista del campo en distribución analítica de líneas de factura
- ✅ Prioridad de asignación: pedido > cabecera factura

### Versión 15.0.1.2.0 (Anterior)
- Añadido propagación a líneas analíticas con distribución
- Mejoras en vistas de apuntes analíticos

### Versión 15.0.1.1.0 (Inicial)
- Implementación base del campo `sale_partner_id`
- Propagación desde pedido a factura a analítica

## 👥 Contribuidores

- **KLO Ingeniería Informática S.L.L.** - Desarrollo y mantenimiento
- Basado en concepto original de Ecosoft Co., Ltd (2019)

## 📞 Soporte

**Contacto**: KLO Ingeniería Informática S.L.L.  
**Website**: https://www.klo.es  
**Versión del documento**: 1.1  
**Fecha**: 2026-04-10

---

**Nota**: Este documento forma parte de la documentación técnica interna de KLO para módulos de Odoo 15.

