# Technical Context — `klo_timesheet_partner_project_filter`

## Módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_timesheet_partner_project_filter` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Ubicación** | `extra-addons/klo/extra/klo_timesheet_partner_project_filter/` |

## Descripción

Módulo independiente para Partes de horas que:
- Añade el cliente (`partner_id`) a la línea de parte de horas, listando primero las empresas.
- Filtra el desplegable de Proyecto para excluir los proyectos finalizados (`project_status.is_closed = False`), tanto al elegir proyecto directamente como al elegirlo por cliente.
- Oculta por defecto la columna de pedido de venta (`so_line`).

## Campo(s) añadido(s)

| Modelo | Campo | Tipo | String | Comportamiento |
|---|---|---|---|---|
| `account.analytic.line` | `partner_id` | Many2one a `res.partner` | Partner | Cliente de la línea; dominio a empresas o contactos sin empresa matriz; empresas primero (contexto `klo_company_first`) |
| `account.analytic.line` | `project_id_id` | Integer (related `project_id.id`) | — | Técnico, para referencia/búsqueda |

## Dependencias

| Módulo | Propósito |
|---|---|
| `hr_timesheet` | Líneas analíticas / partes de horas |
| `hr_timesheet_begin_end` | Campos `time_start`/`time_stop` |
| `project_status` (OCA) | Campo `project_status` y booleano `is_closed` para excluir finalizados |
| `sale_timesheet` | Campo `so_line` (columna que se oculta por defecto) |

## Lógica

- `models/hr_timesheet.py` (`account.analytic.line`):
  - Campo `partner_id` con `compute=None` (cliente manual, no autocompletado) + `context={'klo_company_first': True}`.
  - Campo `project_id` redefinido con **dominio string** y operador `=?`:
    `['&', ('allow_timesheets', '=', True), '&', ('partner_id', '=?', partner_id), '|', ('project_status', '=', False), ('project_status.is_closed', '=', False)]`.
    → Si la línea tiene cliente, solo proyectos de ese cliente; si no, todos. Excluye siempre los finalizados.
  - `default_get`: deja `project_id` vacío al crear una línea nueva (elimina el "proyecto favorito" del base).
  - `onchange_project_id`: al asignar un proyecto, rellena `partner_id` con el cliente del proyecto.
  - `onchange_date`: propone hora/minuto actual como `time_start`/`time_stop`.
- `models/res_partner.py` (`res.partner`): `name_search` (con `@api.readonly`) con contexto `klo_company_first` ordena empresas primero y, dentro de ellas, primero las de nivel superior (`parent_id.id nulls first`).

## Vistas modificadas

| Vista base heredada | Fichero | Qué se añade/cambia |
|---|---|---|
| `hr_timesheet.hr_timesheet_line_tree` | `views/hr_analytic_timesheet.xml` | `partner_id` e `Id proyecto` antes de Proyecto; `time_start`/`time_stop` visibles por defecto; `so_line` oculta por defecto |

## Estructura de archivos

```
klo_timesheet_partner_project_filter/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── hr_timesheet.py
│   └── res_partner.py
├── views/
│   └── hr_analytic_timesheet.xml
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d <db_name> -i klo_timesheet_partner_project_filter --stop-after-init
```

## Posibles adaptaciones futuras

- Si se añaden nuevos estados de cierre en `project.status`, verificar que tengan `is_closed` marcado.
- El dominio de `project_id` no incluye el filtro de privacidad (`privacy_visibility`/`message_partner_ids`) del `_domain_project_id` base; solo aplica a no-managers. Si hiciera falta, reintroducirlo combinando el dominio string con un override de `_domain_project_id`.
- Si en el futuro se quiere autocompletar también el cliente al elegir una tarea (no solo proyecto), añadir un `onchange('task_id')` análogo.
