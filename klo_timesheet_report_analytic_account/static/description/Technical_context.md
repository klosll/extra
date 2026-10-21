# Technical Context — `klo_timesheet_report_analytic_account`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_timesheet_report_analytic_account` |
| **Nombre legible** | KLO - Informe de partes de horas por cuenta analítica |
| **Versión** | `18.0.1.0.0` |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | `Timesheets` |
| **Dependencias** | `hr_timesheet`, `analytic` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_timesheet_report_analytic_account/` |
| **Fecha creación** | 2026-10-21 |
| **Odoo versión** | 18.0 Community |

---

## Descripción

Restaura el desglose **por cuenta analítica** dentro de cada empleado en el informe de
partes de horas (**Partes de horas → Informes → Por empleado**), tal y como existía en v15.

En v15 el informe se basaba directamente en `account.analytic.line`, que sí tenía el campo
`account_id`, por lo que el panel dinámico permitía desplegar cada empleado por su cuenta
analítica. En v18 el informe usa el modelo **`timesheets.analysis.report`** (una vista SQL
sobre `account_analytic_line`, ver `addons/hr_timesheet/report/timesheets_analysis_report.py`)
que **no expone la columna `account_id`**: al no existir el campo en el modelo, no aparece en
"Agrupar por" ni se puede añadir como nivel de fila en el pivot.

Este módulo añade `account_id` al modelo del informe y lo coloca como segundo nivel de fila
en el pivot "Por empleado" (empleado → cuenta analítica, con columnas por mes), además de
habilitar filtro/agrupación por cuenta analítica en todos los informes de partes de horas.

Uso típico: al cierre de mes, filtrar por el mes y obtener las **horas imputadas por
empleado y cuenta analítica** (expandiendo cada empleado en el pivot), con exportación a
Excel desde el botón de descarga del panel dinámico.

---

## Campo(s) añadido(s)

### `timesheets.analysis.report.account_id`

| Atributo | Valor |
|---|---|
| **Modelo** | `timesheets.analysis.report` (vista SQL, `_auto = False`) |
| **Tipo** | `Many2one` → `account.analytic.account` |
| **String** | `Cuenta analítica` |
| **readonly** | `True` |
| **Origen** | Columna `account_id` de `account_analytic_line` (la cuenta analítica del proyecto del parte de horas) |

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `hr_timesheet` | Define `timesheets.analysis.report`, los informes (pivot/graph/list) y los menús de Informes |
| `analytic` | Define `account.analytic.account` y `account.analytic.line.account_id` |

Rutas relevantes:
- `/opt/odoo18_desarrollo/odoo/addons/hr_timesheet/report/timesheets_analysis_report.py`
- `/opt/odoo18_desarrollo/odoo/addons/hr_timesheet/report/hr_timesheet_report_view.xml`

---

## Lógica

### `timesheets.analysis.report._select()` — override

```python
@api.model
def _select(self):
    return super()._select() + """,
        A.account_id AS account_id
    """
```

El modelo del informe se reconstruye en `init()` a partir de `_select() + _from() + _where()`.
El patrón es el mismo que usan `sale_timesheet`, `hr_timesheet_sheet`, `helpdesk_mgmt_timesheet`
o `hr_timesheet_day_week`: **siempre `super()._select()` + columnas propias**, de forma que las
columnas de todos los módulos se acumulan y la vista SQL se recrea al instalar/actualizar.

**Compatibilidad con `sale_timesheet`** (instalado en esta BD): ese módulo sobreescribe
`_table_query` envolviendo `_select()/_from()/_where()` en un subquery `SELECT A.*, ... FROM (...) A`;
nuestra columna queda incluida en el subquery y sigue disponible. No hace falta nada más.

La cuenta analítica de los partes de horas se rellena automáticamente desde el proyecto al
crear/escribir la línea (`account.analytic.line._timesheet_preprocess_get_accounts` en
`addons/hr_timesheet/models/hr_timesheet.py`), por lo que `account_id` siempre está informada
en los partes con proyecto.

---

## Vistas modificadas

### 1. `klo_timesheet_report_analytic_account.timesheets_analysis_report_pivot_employee_analytic_account`

**Hereda:** `hr_timesheet.timesheets_analysis_report_pivot_employee` (pivot del informe "Por empleado")

```xml
<field name="employee_id" position="after">
    <field name="account_id" type="row"/>
</field>
```

**Motivo:** el pivot queda con filas `employee_id` → `account_id` y columnas `date` (mes).
Cada empleado se puede **desplegar** para ver las horas por cuenta analítica, igual que en v15.

### 2. `klo_timesheet_report_analytic_account.timesheets_analysis_report_search_analytic_account`

**Hereda:** `hr_timesheet.hr_timesheet_report_search` (búsqueda de los 3 informes: Por empleado / Por proyecto / Por tarea)

- Añade `<field name="account_id"/>` tras `project_id` (permite filtrar por cuenta analítica).
- Añade el filtro de agrupación `groupby_account` (`{'group_by': 'account_id'}`) en el grupo "Agrupar por...".

**Motivo:** poder agrupar/filtrar por cuenta analítica de forma puntual también en gráficos y
en los informes por proyecto/tarea, sin cambiar sus vistas por defecto.

### 3. `klo_timesheet_report_analytic_account.timesheets_analysis_report_list_analytic_account`

**Hereda:** `hr_timesheet.timesheets_analysis_report_list` (lista de detalle de los informes)

- Añade `<field name="account_id" optional="show"/>` tras `project_id`.

**Motivo:** al hacer drill-down desde el pivot o al ver el detalle, se identifica la cuenta
analítica de cada apunte.

---

## Estructura de archivos

```
klo_timesheet_report_analytic_account/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── timesheets_analysis_report.py   # campo account_id + override de _select()
├── views/
│   └── timesheets_analysis_report_views.xml  # pivot, búsqueda y lista
└── static/
    └── description/
        ├── icon.png                    # icono compartido de KLO (_templates)
        └── Technical_context.md
```

---

## Comportamiento esperado

| Situación | Resultado |
|---|---|
| Partes de horas → Informes → Por empleado | El pivot muestra cada empleado desplegable por cuenta analítica, con las horas por mes |
| Cierre de mes | Filtrar por el mes (campo Fecha); exportar a Excel con el botón de descarga del pivot |
| Informe por proyecto / por tarea / gráficos | "Agrupar por... → Cuenta analítica" disponible |
| Partes de horas sin cuenta analítica | Aparecen con cuenta analítica vacía (fila en blanco) |

---

## Instalación / Actualización

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d klo_dev18 \
    -i klo_timesheet_report_analytic_account \
    --stop-after-init
```

(Para actualizaciones posteriores: `-u klo_timesheet_report_analytic_account` en lugar de `-i`.)

---

## Posibles adaptaciones futuras

- Añadir también la cuenta analítica como fila por defecto en el pivot **Por proyecto** o en el gráfico **Por empleado**.
- Desglosar por **plan analítico** completo (`auto_account_id` / columnas por plan) si se usan varios planes además del plan "Proyectos".
- Informe imprimible en PDF de cierre mensual (empleado × cuenta analítica) si se necesita un documento formal además del pivot/Excel.
- Añadir el campo al formulario del informe (`timesheets_analysis_report_form`).

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-21 | Versión inicial: campo `account_id` en el informe y desglose por cuenta analítica en el pivot "Por empleado" |
