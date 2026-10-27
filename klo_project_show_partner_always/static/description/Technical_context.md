# Technical Context — `klo_project_show_partner_always`

## Módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_project_show_partner_always` |
| **Versión** | `18.0.1.0.0` |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_project_show_partner_always/` |

---

## Descripción

El módulo núcleo `sale_project` añade `invisible="not allow_billable"` al campo `partner_id` ("Cliente") del modelo `project.project`, tanto en el formulario como en la lista de proyectos. Como resultado, los proyectos con `allow_billable=False` ocultan el campo Cliente (y su etiqueta) en el formulario, y muestran la celda de la columna "Cliente" vacía en la lista, aunque `partner_id` esté relleno en base de datos.

Este módulo anula ese atributo `invisible` en ambas vistas para que el **cliente se muestre siempre**, independientemente de si el proyecto es facturable o no.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale_project` | Es el módulo cuyo override sobre `partner_id` queremos neutralizar. Dependemos de él para garantizar que nuestra herencia se aplica después y gana el atributo `invisible`. |

`project` se carga de forma transitiva a través de `sale_project`.

---

## Lógica

No se añaden ni modifican modelos Python. La funcionalidad se limita a dos registros de `ir.ui.view` que heredan las vistas base de `project` y sobreescriben el atributo `invisible` del campo `partner_id`:

```xml
<xpath expr="//field[@name='partner_id']" position="attributes">
    <attribute name="invisible">False</attribute>
</xpath>
```

Se utiliza `priority="100"` en ambos registros para asegurar que el override se aplica con posterioridad al realizado por `sale_project`.

---

## Vistas modificadas

### 1. Formulario de proyecto

| Atributo | Valor |
|---|---|
| **XML-ID de la vista base** | `project.edit_project` |
| **XML-ID del override** | `view_project_form_show_partner_always` |
| **Modelo** | `project.project` |
| **Prioridad** | `100` |
| **Cambio** | Fija `invisible="False"` en el campo `partner_id`, anulando `invisible="not allow_billable"` de `sale_project`. |

### 2. Lista de proyectos

| Atributo | Valor |
|---|---|
| **XML-ID de la vista base** | `project.view_project` |
| **XML-ID del override** | `view_project_list_show_partner_always` |
| **Modelo** | `project.project` |
| **Prioridad** | `100` |
| **Cambio** | Fija `invisible="False"` en la columna `partner_id`, anulando el mismo atributo de `sale_project`. |

---

## Estructura de archivos

```
klo_project_show_partner_always/
├── __init__.py
├── __manifest__.py
├── views/
│   └── project_project_views.xml
└── static/description/
    ├── icon.png
    └── Technical_context.md        ← Este fichero
```

> **Nota:** Este módulo es **solo de vistas** y no contiene carpeta `models/` ni código Python de modelos.

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d klo_dev18 -i klo_project_show_partner_always --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d klo_dev18 -u klo_project_show_partner_always --stop-after-init
```

---

## Posibles adaptaciones futuras

- **Aplicar el mismo criterio a otras vistas de `project.project`** (por ejemplo, vistas kanban, pivot o graph) si en alguna de ellas `sale_project` u otro módulo vuelve a ocultar `partner_id` en función de `allow_billable`.
- **Condicionar la visibilidad por grupos** si en el futuro se decide que solo ciertos perfiles de usuario vean el cliente siempre visible.
- **Extender a `project.task`** si surge la necesidad de mostrar el cliente relacionado en tareas independientemente de la configuración facturable del proyecto.
