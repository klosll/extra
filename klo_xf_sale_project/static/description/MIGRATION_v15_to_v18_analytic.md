# MIGRATION v15 -> v18 — Cuenta analítica en project.project (`klo_xf_sale_project`)

> Documento de migración para la sesión **"Plan actualización Odoo 15 a 18"**.
> Módulo: `klo_xf_sale_project` — versión `18.0.1.1.1` — fecha `2026-09-25`.
> Solo documentación. No modifica lógica. No ejecutar `-u` desde este documento sin confirmación.

---

## 1. Objetivo

Migrar la cuenta analítica de proyecto desde Odoo 15 a Odoo 18 sin perder el enlace
proyecto <-> cuenta analítica y sin romper el núcleo de Odoo 18:

- En v18 el campo nativo `project.project.account_id` se conserva pero queda oculto
  (`invisible=1` en `views/project.xml`, backup invisible).
- El campo Studio legacy `project.project.x_plan4_id` ("Legacy") se quita de la vista
  en v18.0.1.1.1 (2026-09-25): datos ya migrados (`analytic_account_id` 1727/1727,
  caso 2735=75/82/75, backup `/tmp/backup_analytic_20260925.csv`), listo para DROP de columna.
  Se mantiene `pop('x_plan4_id')` defensivo en `models/project.py` por si llega valor de caché.
- El campo nuevo y principal es `project.project.analytic_account_id`
  (Many2one a `account.analytic.account`, `copy=False`, `ondelete=set null`,
  dominio por `company_id`, grupo `analytic.group_analytic_accounting`).
- La migración de datos se hace por `post_init_hook`
  `_post_init_migrate_analytic_account` en `hooks.py` (solo copia
  `account_id` -> `analytic_account_id` donde el nuevo está vacío).

---

## 2. Mapeo v15 -> v18

| Origen v15 | Destino v18 | Notas |
|------------|-------------|-------|
| `project.project.account_analytic_account` (o cuenta analítica usada en v15) | `project.project.account_id` (nativo v18) | La importación OpenUpgrade / CSV carga aquí. Ejemplo global verificado: `1727/1727` coinciden en `account_id` y `x_plan4_id`. |
| — | `project.project.x_plan4_id` ("Legacy", Studio, Many2one a `account.analytic.account`) | Campo manual heredado. Ejemplo global: `1/1727` (solo 1 proyecto usa `x_plan4_id` de 1727). Eliminado de la vista en v18.0.1.1.1, listo para DROP. No usar como destino. |
| — | `project.project.analytic_account_id` (nuevo KLO) | Destino final. Lo rellena el `post_init_hook` copiando desde `account_id`. Se usa en `_prepare_sale_order` con fallback `analytic_account_id or account_id`. |
| Caso proyecto `2735` | `account_id=75` vs `x_plan4_id=82` | Conflicto conocido. Valor correcto: `account_id=75`. El `82` de `x_plan4_id` se revisa manual y no se importa ni se copia. |

Resumen:

- v15 `account_analytic_account` -> v18 `account_id` (ej. `1727/1727` OK).
- v18 `x_plan4_id` Legacy `1/1727` (residual, no fiable).
- Proyecto `2735`: `75` (account_id, correcto) vs `82` (x_plan4_id, revisar manual).

---

## 3. Procedimiento importación

1. Importar la cuenta analítica v15 en el campo nativo v18 `account_id`.
   - No importar directamente en `analytic_account_id` ni en `x_plan4_id`.
   - `x_plan4_id` no se toca (legacy oculto).
2. Instalar / actualizar el módulo para que se cree `analytic_account_id`:
   - Primera instalación ejecuta el `post_init_hook` y copia
     `account_id` -> `analytic_account_id` solo donde `analytic_account_id` está vacío.
   - Las actualizaciones (`-u`) NO re-ejecutan el hook.
3. Caso `2735`:
   - Mantener `account_id=75` como valor correcto.
   - El valor `82` en `x_plan4_id` se revisa manualmente en la ficha del proyecto.
   - No se borran columnas durante la migración.
4. Verificar con los SQL del apartado 4 antes de dar por buena la migración.
5. El filtrado defensivo en `_prepare_sale_order` / `_prepare_sale_order_line`
   (`pop('x_plan4_id')` + conservación solo de claves en `_fields`) evita
   "Campos no válidos: Legacy" al crear pedidos desde el proyecto aunque
   `x_plan4_id` siga en BD.

---

## 4. SQL verificación

Ejecutar con `psql` sobre la BD activa (`klo_dev18`, ver `config/odoo.conf`):

```sql
-- 4.1 Conteos pre/post migración (los mismos que loguea el hook)
SELECT COUNT(*) AS account_id_informados
FROM project_project WHERE account_id IS NOT NULL;

SELECT COUNT(*) AS analytic_account_id_informados
FROM project_project WHERE analytic_account_id IS NOT NULL;

SELECT COUNT(*) AS pendientes_de_migrar
FROM project_project
WHERE analytic_account_id IS NULL AND account_id IS NOT NULL;

-- 4.2 Caso 2735 (conflicto 75 vs 82)
SELECT id, name, account_id, x_plan4_id, analytic_account_id
FROM project_project
WHERE id = 2735 OR name ILIKE '%2735%';

-- 4.3 Divergencias account_id vs x_plan4_id (detectar legados distintos)
SELECT id, name, account_id, x_plan4_id, analytic_account_id
FROM project_project
WHERE x_plan4_id IS NOT NULL
  AND account_id IS DISTINCT FROM x_plan4_id;

-- 4.4 Verificación post-migración (debe dar 0 pendientes)
SELECT COUNT(*) AS pendientes_post
FROM project_project
WHERE analytic_account_id IS NULL AND account_id IS NOT NULL;

-- 4.5 Conflictos ambos informados y distintos (revisión manual, no se sobrescribe)
SELECT id, name, account_id, analytic_account_id
FROM project_project
WHERE analytic_account_id IS NOT NULL
  AND account_id IS NOT NULL
  AND analytic_account_id IS DISTINCT FROM account_id;
```

Criterio de aceptación:

- `pendientes_post = 0`.
- `2735` con `account_id=75` y `analytic_account_id=75` tras el hook.
- Divergencias `account_id != x_plan4_id` revisadas manualmente (ej. global `1727/1727` OK, `1/1727` en `x_plan4_id` residual).

---

## 5. Orden borrado futuro (2 fases, NO ejecutar aún)

### Fase 1 — YA HECHA (v18.0.1.1.0 -> v18.0.1.1.1)

- Vista `klo_xf_view_project_form_analytic` (`views/project.xml`, hereda `project.edit_project`, página `analytic`):
  - `account_id` nativo con `invisible=1` (backup invisible, no se borra).
  - v18.0.1.1.0: `x_plan4_id` Studio con `invisible=1` dentro del `group`.
  - v18.0.1.1.1 (2026-09-25): `x_plan4_id` eliminado de la vista. Vista sin referencia a
    `x_plan4_id`, por lo que el DROP de columna ya no romperá la vista.
  - Nuevo `analytic_account_id` visible tras `account_id`.
- Datos verificados: `analytic_account_id` 1727/1727, caso 2735 `account_id=75` /
  `x_plan4_id=82` / `analytic_account_id=75`, backup `/tmp/backup_analytic_20260925.csv`.
- No se borra ninguna columna ni `ir.model.fields` en esta tarea (solo vista + docs + versión).

### Fase 2 — FUTURA (solo con confirmación + backup)

1. Confirmación explícita del cliente + backup completo de BD.
2. Borrar solo el campo Studio `x_plan4_id`:
   - `unlink` de `ir.model.fields` para `project.project.x_plan4_id`.
   - `DROP COLUMN` de `x_plan4_id` en `project_project` solo si procede
     (verificar que ninguna vista, automatización o export lo usa).
3. NUNCA borrar el `account_id` base:
   - Rompería `company` sync, `rename` propagate, `_check_account_id` y
     `project_ids` (One2many en `account.analytic.account`).
   - Debe permanecer en BD aunque esté invisible en vista.

---

## 6. Comandos

BD activa según `config/odoo.conf`: `db_name = klo_dev18` (no hardcodear otro nombre;
si cambia el entorno, leer `db_name` del fichero). NO ejecutados en esta tarea
(solo documentación, a ejecutar por el agente probador).

```bash
# Instalación (primera vez, SÍ ejecuta post_init_hook account_id -> analytic_account_id)
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d klo_dev18 \
    -i klo_xf_sale_project \
    --stop-after-init

# Actualización (NO re-ejecuta post_init_hook)
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d klo_dev18 \
    -u klo_xf_sale_project \
    --stop-after-init
```

Verificación sintaxis (ya ejecutada en esta tarea):

```bash
python3 -m py_compile \
    /opt/odoo18_desarrollo/extra-addons/klo/extra/klo_xf_sale_project/hooks.py \
    /opt/odoo18_desarrollo/extra-addons/klo/extra/klo_xf_sale_project/models/project.py
```

---

## 7. Nota para sesión "Plan actualización Odoo 15 a 18"

- Este documento es la referencia de migración analítica para dicha sesión.
- Flujo: importar a `account_id` -> instalar (`-i`, hook copia a `analytic_account_id`)
  -> verificar SQL -> caso `2735` fijar `75`, revisar `82` manual.
- Borrado futuro en 2 fases: Fase 1 ya aplicada (invisibles en vista);
  Fase 2 pendiente con confirmación + backup (solo `x_plan4_id`, nunca `account_id`).
