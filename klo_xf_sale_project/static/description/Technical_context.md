# KLO — klo_xf_sale_project

> **Documento técnico para el módulo `klo_xf_sale_project`.**
> Orientado a ser procesado por una IA para futuros ajustes y desarrollos.

---

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_xf_sale_project`                      |
| Nombre legible   | KLO - XF Sale Project Extensions           |
| Versión          | `18.0.1.1.2`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | Project/Project                            |
| Dependencias     | `project`, `sale`, `xf_sale_project`       |
| Ubicación        | `extra-addons/klo/extra/klo_xf_sale_project` |
| Fecha creación   | 2026-09-24                                 |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

Este módulo extiende la funcionalidad del módulo `xf_sale_project` (que vincula proyectos con pedidos de venta) añadiendo:

1. **Corrección en facturas vinculadas**: Redefine el campo `invoice_ids` en `project.project` para incluir **todas** las facturas relacionadas con los pedidos de venta del proyecto. El módulo original solo acumulaba facturas de uno de los pedidos, dejando el resto sin factura asociada.

2. **Plazos de pago en pedidos generados**: Sobrescribe `_prepare_sale_order` para propagar el plazo de pago del cliente (`partner_id.property_payment_term_id`) al pedido de venta creado desde el proyecto.

3. **Cálculo de precios y descuentos en líneas de proyecto**: Reimplementa la lógica de `_get_display_price`, `_get_real_price_currency` y `_onchange_discount` en `project.product.line` para que sea compatible con **Odoo 18**, eliminando el uso del campo obsoleto `discount_policy` en `product.pricelist` y adoptando la nueva API basada en:
   - `product.pricelist._get_product_rule()` / `_get_product_price()`
   - `product.pricelist.item._show_discount()` / `_compute_price_before_discount()` / `_is_discount_feature_enabled()`
   - Grupo `sale.group_discount_per_so_line` (antes `product.group_discount_per_so_line`)

La intención original de mostrar el descuento aplicado por la lista de precios se mantiene intacta, pero ahora usa la arquitectura moderna de Odoo 18.

---

## Estructura de archivos

```
klo_xf_sale_project/
├── __init__.py               # importa models + hooks (_post_init_migrate_analytic_account)
├── __manifest__.py           # version 18.0.1.1.2 + post_init_hook
├── hooks.py                  # migración account_id -> analytic_account_id (post-init)
├── models/
│   ├── __init__.py
│   └── project.py          # Lógica principal: Project, ProjectProductLine
├── views/
│   └── project.xml           # heredadas project.view_project + project.edit_project (página Analytic)
├── static/
│   └── description/
│       ├── icon.png
│       ├── Technical_context.md
│       └── MIGRATION_v15_to_v18_analytic.md
```

---

## Modelos afectados

### `project.project` — Extensión de proyecto

**Archivo:** `models/project.py`  
**Tipo de herencia:** `_inherit`

#### Campos añadidos / modificados

| Campo | Tipo | String | Descripción |
|-------|------|--------|-------------|
| `analytic_account_id` | Many2one a `account.analytic.account` | Cuenta analítica | Nuevo campo principal (copy=False, ondelete=set null, dominio por company_id, grupo `analytic.group_analytic_accounting`). Sustituye a `account_id` (nativo) y `x_plan4_id` (Studio legacy). Se usa en `_prepare_sale_order` con fallback `analytic_account_id or account_id`. |
| `invoice_ids` | Many2many | Invoices | Redefinido para buscar facturas a través de `account.move.line` vinculadas a cualquier pedido del proyecto (`sale_line_ids.order_id.project_id`). El original usaba una relación directa más limitada. |

#### Métodos añadidos / sobreescritos

```python
def _compute_invoice_ids(self):
    """
    Busca líneas de factura (account.move.line) que tengan líneas de pedido
    (sale_line_ids) cuyo pedido pertenezca a este proyecto.
    Asigna la factura completa (move_id) al campo invoice_ids.
    """

def _prepare_sale_order(self):
    """
    Extiende el método del padre para añadir payment_term_id del partner
    al diccionario de valores del pedido de venta.
    Incluye filtrado defensivo contra campos Studio (x_plan4_id "Legacy"):
    solo conserva claves existentes en sale.order._fields.
    """

def _prepare_sale_order_line(self, order):
    """
    Extiende el método del padre para filtrar claves no válidas en
    sale.order.line._fields (pop explícito de x_plan4_id y cualquier x_*).
    Evita "Campos no válidos" al generar líneas desde el proyecto.
    """
```

---

### `project.product.line` — Líneas de producto del proyecto

**Archivo:** `models/project.py`  
**Tipo de herencia:** `_inherit`

#### Métodos añadidos / sobreescritos

```python
def _get_pricelist(self):
    """
    Helper seguro para obtener la lista de precios del partner del proyecto.
    Retorna recordset vacío (no False) si no hay partner o pricelist.
    Usa hasattr/getattr para protección defensiva.
    """

def _pricelist_shows_discount(self, pricelist=None):
    """
    Determina si el pricelist debe mostrar descuento (estilo Odoo 18).
    Delega en product.pricelist.item._show_discount() que comprueba:
    - _is_discount_feature_enabled() -> grupo sale.group_discount_per_so_line
    - compute_price == 'percentage'
    """

def _get_display_price(self, product):
    """
    Calcula el precio de visualización (equivalente a sale.order.line._get_display_price_ignore_combo).
    Flujo:
    1. Obtiene regla de pricelist (_get_product_rule)
    2. Calcula precio final con regla (_compute_price)
    3. Si regla no muestra descuento -> devuelve precio final
    4. Si muestra descuento -> calcula precio base (_compute_price_before_discount)
    5. Retorna max(base_price, pricelist_price) para incluir recargos negativos
    """

def _get_product_price_context(self):
    """
    Contexto para cálculo de precio (atributos no variante).
    Delega en product._get_product_price_context().
    """

def _onchange_discount(self):
    """
    Onchange al cambiar product_id: calcula descuento automático (estilo sale.order.line._compute_discount).
    Solo aplica si:
    - Existe producto, UoM, partner, pricelist
    - Feature descuento habilitada (sale.group_discount_per_so_line)
    - Regla de pricelist es percentage (_show_discount == True)
    Calcula discount = (base_price - pricelist_price) / base_price * 100
    """

def product_id_change(self):
    """
    Onchange estándar: actualiza price_unit usando _get_display_price.
    """
```

---

## Vistas / Templates QWeb modificados

`views/project.xml`:

- `klo_xf_view_project` hereda `project.view_project` (tree): añade `sale_order_ids` e `invoice_ids` (many2many_tags, optional show) antes de `display_name`.
- `klo_xf_view_project_form_analytic` hereda `project.edit_project` (form, página `analytic`):
  - añade `analytic_account_id` tras `account_id` (grupo `analytic.group_analytic_accounting`).
  - `account_id` (nativo) con `invisible=1` (oculto como backup, no borrado: rompería core).
  - `x_plan4_id` (Studio legacy) eliminado de la vista en v18.0.1.1.1 (2026-09-25): datos ya migrados
    (`analytic_account_id` poblado 1727/1727, backup `/tmp/backup_analytic_20260925.csv`), listo para DROP de columna.
    Se mantiene `pop('x_plan4_id')` defensivo en `models/project.py` por si llega valor de caché.
  - v18.0.1.1.2 (2026-09-25): comentarios XML de la vista saneados para no mencionar el nombre técnico
    del campo legacy (usan "campo Studio legacy" genérico). Objetivo: `SELECT ... WHERE arch_db LIKE '%x_plan4_id%'`
    debe dar 0 filas tras `-u`. El `pop` defensivo se mantiene en `models/project.py`.
    Nota caché navegador: si tras el DROP persiste "field is undefined" al abrir desde lista,
    forzar recarga dura con Ctrl+Shift+R (o vaciar caché / probar en incógnito).

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Proyecto con múltiples pedidos de venta, cada uno facturado | `invoice_ids` muestra **todas** las facturas de todos los pedidos |
| Crear pedido de venta desde proyecto | El pedido hereda `payment_term_id` del cliente |
| Línea de producto con pricelist de tipo 'percentage' y grupo descuento activo | Se calcula y muestra `discount` automáticamente en `_onchange_discount` |
| Línea de producto con pricelist 'fixed' o 'formula' | `discount` = 0.0 (no hay descuento porcentual que mostrar) |
| Partner sin pricelist asignado | `_get_pricelist` retorna recordset vacío; `_get_display_price` usa `lst_price` del producto |
| Migración desde Odoo ≤17 | El código ya no usa `discount_policy` ni `get_product_price_rule` (eliminados en Odoo 18) |

---

## Dependencias técnicas internas

- `xf_sale_project` — Módulo base que vincula proyectos con pedidos de venta; este módulo extiende sus modelos
- `sale` — Necesario para `sale.group_discount_per_so_line` y la API de pricelist
- `project` — Modelo base extendido

---

## Notas para IA / desarrollador

- **Campo clave:** `project.project.invoice_ids` — Many2many computado que busca en `account.move.line` para encontrar **todas** las facturas de **todos** los pedidos del proyecto.
- **Método clave:** `ProjectProductLine._get_display_price` — Réplica la lógica de `sale.order.line._get_display_price_ignore_combo` adaptada a `project.product.line`. Usa la nueva API de pricelist de Odoo 18.
- **Método clave:** `ProjectProductLine._onchange_discount` — Réplica `sale.order.line._compute_discount`. Calcula descuento solo si la regla es `percentage` y el grupo `sale.group_discount_per_so_line` está activo.
- **Helper clave:** `ProjectProductLine._get_pricelist` / `_pricelist_shows_discount` — Encapsulan la lógica de compatibilidad Odoo 18 (sin `discount_policy`).
- **Consideraciones:** 
  - El módulo `xf_sale_project` debe estar instalado (dependencia en `__manifest__.py`).
  - No se crean nuevos campos en BD, solo se redefinen computados y lógica.
  - La conversión de moneda en `_get_real_price_currency` (método legacy) ya no se usa; la nueva API de pricelist maneja conversiones internamente via `_compute_price` y `_compute_price_before_discount` recibiendo `currency` como parámetro.

---

## Instalación y actualización

Instalación (nueva BD o primera instalación, ejecuta `post_init_hook`):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -i klo_xf_sale_project \
    --stop-after-init
```

Actualización (cambios de código/vistas, NO re-ejecuta `post_init_hook`):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_xf_sale_project \
    --stop-after-init
```

> Nota: la BD activa es la definida por `db_name` en `config/odoo.conf`. No hardcodear el nombre.

---

## Migración account_id -> analytic_account_id (post_init_hook)

**Fecha:** 2026-09-25
**Hook:** `_post_init_migrate_analytic_account(env)` en `hooks.py`, expuesto en `__init__.py`, declarado en `__manifest__.py` como `post_init_hook`. Versión `18.0.1.1.1`.

- Recibe `api.Environment`.
- Backup de conteos vía log con `SELECT COUNT(*)`: nativos informados (`account_id IS NOT NULL`), nuevos informados (`analytic_account_id IS NOT NULL`), pendientes (`analytic_account_id IS NULL AND account_id IS NOT NULL`).
- Copia ORM: `search([('analytic_account_id','=',False),('account_id','!=',False)])` + `write({'analytic_account_id': account_id.id})`. Solo donde el nuevo está vacío.
- Conflictos (ambos informados y distintos): solo `log warning`, no se sobrescribe.
- Caso 2735 / cuentas 75 vs 82: `log warning` específico; valor correcto `account_id=75`, no se borran columnas.
- Verificación: `python3 -m py_compile` de todos los `.py` del módulo. No se ejecuta `-u`.

Ver detalle en `static/description/MIGRATION_v15_to_v18_analytic.md`.

---

## Fix defensivo campo Studio "Legacy" (x_plan4_id)

**Fecha:** 2026-09-24
**Contexto:** Al confirmar el proyecto 2735 con K502 se producía el error
"Campos no válidos: Legacy". El campo Studio `project.project.x_plan4_id`
(label "Legacy", many2one a `account.analytic.account`, required=False)
no es usado por ninguna vista, pero su valor se propagaba al crear
`sale.order` desde `action_create_sale_order` (módulo `xf_sale_project`),
donde `sale.order` no tiene ese campo -> `Invalid fields`.

**Solución (solo en `klo_xf_sale_project`, sin tocar Studio ni borrar columnas):**
- `Project._prepare_sale_order`: tras `super()` + `payment_term_id`, hace
  `pop('x_plan4_id')` explícito y filtra el diccionario conservando solo
  claves presentes en `self.env['sale.order']._fields` (descarta cualquier
  otro `x_*` no permitido).
- `ProjectProductLine._prepare_sale_order_line`: nuevo override que llama a
  `super()` y aplica el mismo filtrado contra
  `self.env['sale.order.line']._fields`.
- Comentarios en español, identificadores en inglés.
- Verificación: `python3 -m py_compile models/project.py` OK.
- No se ejecuta `-u` (lo hará el agente probador).

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-09-24 | Migración a Odoo 18: eliminación de `discount_policy`, uso de `_get_product_rule`, `_show_discount`, `_compute_price_before_discount`, `_is_discount_feature_enabled`, grupo `sale.group_discount_per_so_line`. Helpers `_get_pricelist` y `_pricelist_shows_discount`. |
| 18.0.1.0.1 | 2026-09-24 | Fix "Legacy": filtrado defensivo en `_prepare_sale_order` y `_prepare_sale_order_line` contra `x_plan4_id` y `x_*` no presentes en `sale.order` / `sale.order.line`. |
| 18.0.1.1.0 | 2026-09-25 | Campo `analytic_account_id` (Cuenta analítica) + migración `post_init_hook` (`account_id` -> `analytic_account_id`) + vista form con `account_id` y `x_plan4_id` en invisible. |
| 18.0.1.1.1 | 2026-09-25 | `x_plan4_id` eliminado de la vista (id 4617 `klo.xf.project.form.analytic`): solo `account_id` invisible (backup) + `analytic_account_id` visible. Datos verificados (`analytic_account_id` 1727/1727, caso 2735=75/82/75, backup `/tmp/backup_analytic_20260925.csv`). Listo para DROP de columna en BD. Se mantiene `pop('x_plan4_id')` defensivo en `models/project.py`. Sin `-u` ni DROP en esta tarea. |
| 18.0.1.1.2 | 2026-09-25 | Saneado de comentarios XML en `views/project.xml` (id 4617): ya no mencionan el nombre técnico del campo legacy (usan "campo Studio legacy" genérico) para que `arch_db LIKE '%x_plan4_id%'` dé 0 filas tras `-u`. Se mantiene `pop` defensivo en `models/project.py`. Nota caché navegador: forzar Ctrl+Shift+R si persiste "field is undefined" por arch antigua en caché. Sin `-u` ni DROP en esta tarea. |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)