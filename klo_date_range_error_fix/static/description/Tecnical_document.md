# Documento Técnico — klo_date_range_error_fix (Odoo 15)

## Propósito

Módulo corrector del bug de **zona horaria** en el módulo OCA `date_range` (v15).

Corrige los métodos `_setDefaultValue` y `onValueChange` del parche JS que `date_range` aplica sobre el componente legacy `web.CustomFilterItem`. El bug de OCA provocaba que al seleccionar un rango de fechas en el diálogo de "Filtro personalizado", los datos del día anterior al inicio del rango aparecieran incorrectamente en los resultados.

---

## Módulo que corrige

**OCA:** `date_range` (server-ux)
**Archivo afectado:** `extra-addons/oca/server-ux/date_range/static/src/js/date_range.esm.js`
**Métodos afectados:** `_setDefaultValue` y `onValueChange` en el parche `"date_range.CustomFilterItem"`

---

## Descripción del bug original

### Escenario que lo activa

1. Se archivan (`active=False`) los rangos de fechas de años anteriores (p.ej. todos los de 2024 y 2025).
2. El `search_read` de `date.range` en `_computeDateRangeOperators` excluye registros inactivos por defecto.
3. El primer rango activo visible para el tipo "Mensual" pasa a ser **M01-26** (2026-01-01 a 2026-01-31).
4. Cuando el usuario selecciona el operador **"in Mensual"** en el filtro personalizado, `_setDefaultValue` establece M01-26 como valor por defecto.
5. Como M01-26 **ya aparece seleccionado** en el dropdown, el usuario no lo cambia → `onValueChange` (que sí usa `moment.utc()`) **nunca se ejecuta**.
6. Al hacer clic en "Aplicar", `onApply` usa los valores incorrectos de `_setDefaultValue`.

### Líneas problemáticas en `date_range.esm.js`

```javascript
// ANTES (buggy - usa hora local del navegador)
const d_start = moment(`${default_range.date_start} 00:00:00`);
const d_end = moment(`${default_range.date_end} 23:59:59`);
```

### Flujo técnico de la conversión de fechas

```
moment('2026-01-01 00:00:00')           ← Moment LOCAL del navegador
  → field_utils.parse.date(localMoment)
  → internamente: moment.utc(localMoment)  ← convierte a UTC
  → España UTC+1 (invierno CET):  2025-12-31T23:00:00Z → .format('YYYY-MM-DD') → '2025-12-31' ❌
  → España UTC+2 (verano CEST):   2025-12-31T22:00:00Z → .format('YYYY-MM-DD') → '2025-12-31' ❌
  → VPS Alemania UTC+2 (verano):  2025-12-31T22:00:00Z → .format('YYYY-MM-DD') → '2025-12-31' ❌

moment.utc('2026-01-01 00:00:00')       ← Moment directamente en UTC
  → field_utils.parse.date(utcMoment)
  → internamente: moment.utc(utcMoment)  ← ya es UTC, no cambia
  → cualquier zona horaria:       2026-01-01T00:00:00Z → .format('YYYY-MM-DD') → '2026-01-01' ✓
```

**Dominio generado (incorrecto):**
```python
[('date', '>=', '2025-12-31'), ('date', '<=', '2026-01-31')]
# Incluye datos del 31/12/2025 que NO deberían aparecer
```

**Dominio esperado (correcto):**
```python
[('date', '>=', '2026-01-01'), ('date', '<=', '2026-01-31')]
```

---

## Solución aplicada

### Archivo JS del módulo corrector

`static/src/js/klo_date_range_fix.esm.js`

Aplica un **segundo parche** sobre `CustomFilterItem.prototype` (nombre: `"klo_date_range_error_fix.CustomFilterItem"`) que sobreescribe **ambos métodos** usando `moment.utc()`. Aunque OCA ya usa `moment.utc()` en `onValueChange`, se sobreescribe igualmente para que el parche KLO sea autosuficiente ante futuras actualizaciones de OCA.

```javascript
// CORRECCIÓN (usa UTC explícito)
const d_start = moment.utc(`${default_range.date_start} 00:00:00`);
const d_end = moment.utc(`${default_range.date_end} 23:59:59`);
```

### Cadena de llamadas (`_setDefaultValue`)

```
KLO patch → si date_range: usa moment.utc() y retorna ✓
           → si NO date_range: llama this._super() → OCA patch → llama this._super() → original Odoo
```

El parche KLO intercepta antes que el parche OCA para el caso `date_range`, evitando que el código buggy de OCA se ejecute.

---

## Estructura del módulo

```
klo_date_range_error_fix/
├── __manifest__.py         # depends: ['date_range'], version: 15.0.1.0.1
├── __init__.py
├── static/
│   ├── description/
│   │   ├── icon.png        # Icono KLO
│   │   └── Tecnical_document.md
│   └── src/
│       └── js/
│           └── klo_date_range_fix.esm.js   # Parche corrector
```

---

## Dependencias

| Módulo | Razón |
|---|---|
| `date_range` | OCA module que se corrige; la dependencia garantiza que el JS de OCA cargue primero |

---

## Instalación y activación

```bash
# Instalar el módulo
/opt/odoo15_klo/odoo/odoo-bin -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -i klo_date_range_error_fix --stop-after-init

# Actualizar el módulo (tras cambios)
/opt/odoo15_klo/odoo/odoo-bin -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -u klo_date_range_error_fix --stop-after-init

# Limpiar caché de bundles JS en BD (necesario cuando cambia el manifest)
psql klo_dev -c "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';"

# Luego forzar recarga de assets en el navegador: Ctrl+F5
```

---

## Historial de versiones

### v15.0.1.0.1 — 2026-06-15

**Bug crítico corregido en el manifest:**
El archivo `__manifest__.py` referenciaba la ruta del asset JS con el nombre antiguo del módulo (`klo_date_range_error_correction/static/src/js/klo_date_range_fix.esm.js`) en lugar del nombre actual (`klo_date_range_error_fix/static/src/js/klo_date_range_fix.esm.js`). Esto provocaba que el JS corrector **nunca se cargara** en ningún entorno, haciendo que la corrección fuera completamente inoperativa.

Contexto: el módulo fue renombrado de `klo_date_range_error_correction` a `klo_date_range_error_fix` pero la ruta del asset no se actualizó correctamente.

**Mejoras adicionales:**
- Se sobreescribe también `onValueChange` (además de `_setDefaultValue`) para hacer el parche autosuficiente.
- Se limpian los bundles JS cacheados en BD (`ir_attachment`) para forzar regeneración.

**Impacto del bug antes de esta versión:**
- El filtro de date_range mostraba datos del 31/12/2025 al filtrar por M01-26 (enero 2026).
- Afectaba especialmente al VPS en Alemania (mismo UTC+2 que España en verano CEST).
- El bug era idéntico en todos los entornos pero el síntoma era más visible en el VPS del cliente porque allí se hacía la prueba con los rangos de 2025 archivados.

### v15.0.1.0.0 — 2026-05-21

Creación inicial del módulo como corrección al bug de zona horaria en `_setDefaultValue` del módulo OCA `date_range`. Módulo renombrado desde `klo_date_range_error_correction`.

---

## Versión actual y autoría

- **Versión:** 15.0.1.0.1
- **Licencia:** AGPL-3
- **Autor:** KLO Ingeniería Informática S.L.L.
- **Última actualización:** 2026-06-15

---

## Notas para actualizaciones futuras de OCA date_range

Si se actualiza el módulo OCA `date_range` mediante `git pull`, verificar:
1. Si el bug ya fue corregido upstream → este módulo puede desinstalarse.
2. Si el método `_setDefaultValue` cambió su firma → adaptar el parche KLO.
3. El bug fue reportado al upstream como: `_setDefaultValue` uses `moment()` instead of `moment.utc()` causing off-by-one-day timezone errors in UTC+X timezones.
4. Después de actualizar OCA, ejecutar: `psql klo_dev -c "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';"` y recargar el navegador.
