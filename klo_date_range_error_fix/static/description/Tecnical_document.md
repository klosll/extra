# Documento Técnico — klo_date_range_error_fix (Odoo 15)

## Propósito

Módulo corrector del bug de **zona horaria** en el módulo OCA `date_range` (v15).

Corrige el método `_setDefaultValue` del parche JS que `date_range` aplica sobre el componente legacy `web.CustomFilterItem`. El bug de OCA provocaba que al seleccionar un rango de fechas en el diálogo de "Filtro personalizado", los datos del día anterior al inicio del rango aparecieran incorrectamente en los resultados.

---

## Módulo que corrige

**OCA:** `date_range` (server-ux)
**Archivo afectado:** `extra-addons/oca/server-ux/date_range/static/src/js/date_range.esm.js`
**Método afectado:** `_setDefaultValue` en el parche `"date_range.CustomFilterItem"`

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
// ANTES (buggy - usa hora local)
const d_start = moment(`${default_range.date_start} 00:00:00`);
const d_end = moment(`${default_range.date_end} 23:59:59`);
```

### Efecto en España (UTC+1 en invierno / CET)

```
moment('2026-01-01 00:00:00')
  → 2026-01-01T00:00:00+01:00
  → equivalente UTC: 2025-12-31T23:00:00Z
  → field_utils.parseDate() → '2025-12-31'  ← ¡INCORRECTO!
```

**Dominio generado (incorrecto):**
```python
[('date', '>=', '2025-12-31'), ('date', '<=', '2026-01-31')]
# Incluye 263 registros del 31/12/2025 que NO deberían aparecer
```

**Dominio esperado (correcto):**
```python
[('date', '>=', '2026-01-01'), ('date', '<=', '2026-01-31')]
```

---

## Solución aplicada

### Archivo JS del módulo corrector

`static/src/js/klo_date_range_fix.esm.js`

Aplica un **segundo parche** sobre `CustomFilterItem.prototype` (nombre: `"klo_date_range_error_fix.CustomFilterItem"`) que sobreescribe `_setDefaultValue` usando `moment.utc()`:

```javascript
// DESPUÉS (correcto - usa UTC)
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
├── __manifest__.py         # depends: ['date_range']
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

# Luego forzar recarga de assets en el navegador: Ctrl+F5
```

---

## Versión y autoría

- **Versión:** 15.0.1.0.0
- **Licencia:** AGPL-3
- **Autor:** KLO Ingeniería Informática S.L.L.
- **Fecha creación:** 2026-05-21

---

## Notas para actualizaciones futuras de OCA date_range

Si se actualiza el módulo OCA `date_range` mediante `git pull`, verificar:
1. Si el bug ya fue corregido upstream → este módulo puede desinstalarse.
2. Si el método `_setDefaultValue` cambió su firma → adaptar el parche KLO.
3. El bug fue reportado al upstream como: `_setDefaultValue` uses `moment()` instead of `moment.utc()` causing off-by-one-day timezone errors in UTC+X timezones.

