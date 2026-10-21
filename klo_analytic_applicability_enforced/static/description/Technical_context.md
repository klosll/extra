# KLO — Aplicabilidad del plan analítico en apuntes contables

---

## Identificación del módulo

| Campo            | Valor                                      |
|------------------|--------------------------------------------|
| Nombre técnico   | `klo_analytic_applicability_enforced`      |
| Nombre legible   | KLO - Aplicabilidad del plan analítico en apuntes contables |
| Versión          | `18.0.1.0.0`                               |
| Autor            | KLO Ingeniería Informática S.L.L.          |
| Licencia         | AGPL-3                                     |
| Categoría        | `Accounting/Accounting`                    |
| Dependencias     | `account`                                  |
| Ubicación        | `extra-addons/klo/extra/klo_analytic_applicability_enforced` |
| Fecha creación   | `2026-10-19`                               |
| Odoo versión     | 18.0 Community                             |

---

## Descripción funcional

En Odoo la **Aplicación (applicability) del plan analítico** solo se evalúa en la
interfaz: decide si la columna de cuenta analítica se muestra, es obligatoria o no
está disponible para una cuenta contable (reglas por `business_domain` y
`account_prefix` dentro del plan). **No se valida al guardar**.

Eso provoca el "pegote" de cuenta analítica: si una línea llega a tener una
distribución analítica (al cambiar la cuenta contable de la línea —p. ej. de 705 a
438—, por un modelo de distribución analítica, por propagación desde una línea de
venta/compra o por importación), el widget muestra el plan igualmente (comportamiento
"forced plans" de `get_relevant_plans`) y el valor se guarda, aunque el plan esté
configurado como **No disponible** para esa cuenta.

Este módulo hace que la aplicabilidad sea **efectiva también al guardar**: si el plan
analítico no está disponible para la cuenta contable de la línea, esa parte de la
distribución analítica se retira automáticamente. Con la configuración del plan
"Proyecto Analíticos" (aplicabilidad por defecto *No disponible* y reglas que permiten
los prefijos `6,7`), el resultado es que **solo las cuentas de los grupos 6 y 7 pueden
llevar cuenta analítica**, en facturas de cliente, facturas de proveedor y asientos
manuales.

Actúa sobre `account.move.line` (apuntes contables) y sobre `account.move` (al
contabilizar).

---

## Estructura de archivos

```
klo_analytic_applicability_enforced/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── account_move.py            # Limpieza antes de contabilizar (_post)
│   └── account_move_line.py       # Lógica de aplicabilidad y limpieza
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Campo(s) añadido(s)

Ninguno. El módulo solo añade métodos de negocio sobre los modelos existentes.

---

## Dependencias

- `account` (Odoo core) — aporta `account.move`, `account.move.line` y la extensión
  de `account.analytic.applicability` con el criterio `account_prefix`.
- `analytic` (Odoo core, indirecto) — modelos `account.analytic.plan`,
  `account.analytic.applicability`, `account.analytic.account` y `analytic.mixin`.

---

## Lógica

**Archivo:** `models/account_move_line.py` — `_inherit = "account.move.line"`

| Método | Tipo | Descripción |
|--------|------|-------------|
| `_klo_should_enforce_analytic_applicability()` | nuevo | Devuelve `True` salvo en líneas de asientos ya contabilizados (`parent_state == 'posted'`): la historia contable no se toca. |
| `_klo_analytic_business_domain()` | nuevo | Devuelve `'invoice'`, `'bill'` o `'general'` según el tipo de documento, igual que hace el core en `_validate_analytic_distribution`. |
| `_klo_applicable_analytic_distribution()` | nuevo | Devuelve la distribución analítica de la línea depurada: para cada clave (p. ej. `"39"` o `"12,13"`) toma sus cuentas analíticas y sus planes raíz (`root_plan_id`) y descarta la clave si algún plan queda en `unavailable` con los criterios `business_domain`, `product`, `account` y `company_id`. La aplicabilidad se evalúa **con la compañía de la línea** (`plan.with_company(line.company_id)`). Las líneas de tipo sección/nota devuelven `{}` (nunca analítica) y las líneas sin cuenta contable se dejan intactas hasta que la tengan. |
| `_klo_sanitize_analytic_distribution()` | nuevo | Escribe la distribución permitida en las líneas que se han quedado con valores no permitidos (con el contexto `klo_skip_analytic_sanitize` para no recursar). |
| `_compute_analytic_distribution()` | sobreescrito | Tras el `super()` (modelos de distribución analítica / distribución relacionada), aplica `_klo_applicable_analytic_distribution()`. Mantiene los mismos `@api.depends('account_id', 'partner_id', 'product_id')` que el core. |
| `create()` | sobreescrito | Tras crear, sanea las líneas creadas (importaciones, propagación desde venta/compra...). |
| `write()` | sobreescrito | Tras escribir, sanea si se ha tocado `account_id` o `analytic_distribution` (cambio de cuenta en la interfaz). |

**Archivo:** `models/account_move.py` — `_inherit = "account.move"`

| Método | Tipo | Descripción |
|--------|------|-------------|
| `_post()` | sobreescrito | Sanea `line_ids` **antes** de `super()._post()`, de modo que `_create_analytic_lines()` nunca genere apuntes analíticos sobre cuentas no permitidas (importante en borradores que se contabilizan sin haberse editado). |

---

## Vistas modificadas

Ninguna. El widget `analytic_distribution` ya oculta el plan cuando la aplicabilidad es
`unavailable` y la línea no trae valor; al impedir que el valor persista, el campo queda
inutilizable en las cuentas no permitidas ("No analytic plans found").

---

## Comportamiento esperado

| Situación | Resultado |
|-----------|-----------|
| Línea de factura con cuenta 438/217 desde el inicio | El plan no aparece; no se puede poner cuenta analítica. |
| Línea con cuenta de ingreso/gasto (7xx/6xx) con analítica y se cambia la cuenta a 438/217 | La cuenta analítica se retira sola al guardar (y también en pantalla, al recomputar). |
| Modelo de distribución analítica que rellena la analítica en una cuenta no permitida | El valor se retira al crear/guardar la línea. |
| Venta/compra que propaga analítica a una línea con cuenta no permitida | El valor se retira al crear la línea. |
| Borrador con "pegotes" que se contabiliza sin editar | La limpieza se aplica en `_post()` antes de crear los apuntes analíticos. |
| Asiento ya contabilizado con analítica en cuenta no permitida | No se toca (historial contable). |

---

## Datos de configuración

El módulo no carga datos. La política concreta vive en la **Aplicación del plan
analítico** (Contabilidad → Configuración → Analítica → Planes analíticos → pestaña
*Aplicabilidad*), que es lo que este módulo hace cumplir. Configuración usada en
`klo_dev18` (plan "Proyecto Analíticos"):

- Aplicabilidad por defecto: **No disponible**.
- Regla `Factura` (`invoice`): prefijos `6,7` → Opcional.
- Regla `Factura de proveedor` (`bill`): prefijos `6,7` → Opcional.
- Regla `Varios` (`general`): prefijos `6,7` → Opcional.

---

## Dependencias técnicas internas

Ninguna sobre otros módulos `klo_*`. Interactúa con:
- `account_analytic_required` (OCA) y `account_analytic_distribution` (Avanzosc), que
  también trabajan con la distribución analítica de `account.move.line`, pero sin
  conflicto: este módulo sanea el valor final de `analytic_distribution`.

---

## Notas para IA / desarrollador

- **Método clave:** `_klo_applicable_analytic_distribution()` en `account.move.line` —
  es la única fuente de la regla; si se quiere cambiar la política (por ejemplo permitir
  cuentas concretas fuera de los grupos 6/7) basta con tocar la aplicabilidad del plan o
  con sobreescritura de este método.
- **`_merge_distribution()` de `analytic.mixin`**: si el nuevo valor no lleva la clave
  `__update__`, sustituye todo el reparto; por eso escribir `False`/`{}` limpia de forma
  efectiva (no fusiona con el valor anterior).
- **Forzado de planes en el widget**: `account.analytic.plan.get_relevant_plans()` muestra
  los planes "unavailable" si la línea ya tiene cuentas analíticas (`existing_account_ids`
  → `forced_plans`). Es el mecanismo que hacía visible el plan en la 438/217; al no dejar
  persistir el valor, el plan desaparece de esas líneas.
- **Multiempresa (importante):** `account.account.code` es un campo **calculado por
  compañía** (`code_store` es `company_dependent` y `_compute_code` lee con
  `self.env.company.root_id`). Evaluado con otra compañía activa devuelve `False`, la
  regla de prefijos no casa y se acabaría retirando una analítica legítima de otra
  empresa. Por eso `_klo_applicable_analytic_distribution()` evalúa siempre con
  `plan.with_company(line.company_id)`. Cualquier extensión de esta lógica debe
  mantener esa regla (afectó a las líneas de la empresa 2 en la primera pasada de
  limpieza de `klo_dev18`, que hubo que restaurar).
- **Consideraciones:**
  - La limpieza es **silenciosa** (no lanza error): el valor se retira solo. Si se
    prefiere bloquear con mensaje de validación, añadir un `@api.constrains` sobre
    `analytic_distribution` y `account_id` en `_klo_sanitize_analytic_distribution`.
  - Solo se actúa sobre líneas **no contabilizadas**. Los apuntes de asientos ya
    publicados conservan su analítica histórica.
  - Las claves de `analytic_distribution` pueden agrupar varias cuentas analíticas
    (`"12,13"`); se descarta la clave completa si algún plan de esas cuentas no está
    disponible.
  - Las líneas de sección/nota no pueden llevar analítica (se retira); las líneas
    **sin cuenta contable** no se tocan para no interferir con la cuenta que llega
    después desde el producto.

---

## Instalación / Actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d klo_dev18 \
    -i klo_analytic_applicability_enforced \
    --stop-after-init
```

(Para actualizaciones posteriores, cambiar `-i` por `-u`.)

---

## Posibles adaptaciones futuras

- Extender el saneado a otros modelos con reparto analítico (`sale.order.line`,
  `purchase.order.line`, `hr.expense`) si se quiere la misma restricción antes de llegar
  al apunte contable.
- Convertir la limpieza silenciosa en error de validación (ver Notas).
- Añadir configuración por compañía (parámetro de sistema o ajustes de contabilidad) en
  lugar de depender solo de la aplicabilidad del plan.

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-19 | Versión inicial. Aplica la aplicabilidad del plan analítico al guardar y al contabilizar. |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
