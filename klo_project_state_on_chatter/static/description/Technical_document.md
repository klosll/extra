# Technical Document — klo_project_state_on_chatter

**Versión:** 15.0.1.0.0  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** AGPL-3  
**Categoría:** Project  
**Ruta:** `extra-addons/klo/extra/klo_project_state_on_chatter/`

---

## 1. Propósito

Este módulo registra automáticamente en el **chatter** del proyecto cada vez que se cambia el estado (`project_status`) desde el widget statusbar. El mensaje incluye:

- Estado anterior
- Nuevo estado
- Fecha del cambio (dd/mm/aaaa)
- Hora del cambio (HH:MM)
- Usuario que realiza el cambio

---

## 2. Estructura de ficheros

```
klo_project_state_on_chatter/
├── __manifest__.py                # Metadatos y dependencias
├── __init__.py                    # Importa models
├── models/
│   ├── __init__.py                # Importa project_project
│   └── project_project.py         # Herencia de project.project
└── static/
    └── description/
        ├── icon.png               # Logo del módulo
        └── Technical_document.md  # Este fichero
```

---

## 3. Mecanismo técnico

### 3.1 Campo `project_status`

El campo `project_status` es un `Many2one` al modelo `project.status`, definido en el módulo OCA `project_status`:

```python
# extra-addons/oca/project/project_status/models/project.py
project_status = fields.Many2one(
    comodel_name="project.status",
    group_expand="_read_group_status_ids",
    copy=False,
    ondelete="restrict",
    index=True,
)
```

El modelo `project.status` contiene registros como:
- **Pending** (`project_status_pending`)
- **In Progress** (`project_status_in_progress`)
- **Complete** (`project_status_complete`)

### 3.2 Detección del cambio

El módulo sobrescribe el método `write()` de `project.project`:

1. **Antes** del `write`: captura el `project_status` actual de cada proyecto afectado en un diccionario `{project_id: old_status}`.
2. Ejecuta `super().write(vals)` para aplicar el cambio real.
3. **Después** del `write`: compara el estado anterior con el nuevo para cada proyecto. Si hay cambio, construye el mensaje y lo publica vía `message_post()`.

```python
def write(self, vals):
    if "project_status" in vals:
        old_statuses = {project.id: project.project_status for project in self}
        result = super().write(vals)
        for project in self:
            if old_statuses[project.id] != project.project_status:
                # ... construir mensaje y project.message_post(body=body)
        return result
    return super().write(vals)
```

### 3.3 Por qué no se usa `tracking=True`

Aunque Odoo ofrece `tracking=True` en campos para registrar automáticamente cambios en el chatter, este enfoque solo muestra "Campo X cambiado de A a B" sin control sobre el formato. El módulo usa `message_post()` directamente para incluir fecha, hora y usuario de forma explícita y legible.

### 3.4 Dependencias

| Módulo | Razón |
|--------|-------|
| `project_status` | Define el campo `project_status` y el modelo `project.status` (OCA) |

`project.project` ya hereda `mail.thread` del núcleo de Odoo, por lo que `message_post()` está disponible sin dependencias adicionales.

---

## 4. Instalación

```bash
/opt/odoo15_klo/odoo/odoo-bin \
  -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -i klo_project_state_on_chatter --stop-after-init
```

---

## 5. Ejemplo de mensaje en el chatter

```
Cambio de estado del proyecto:
De Pending a In Progress
Fecha: 07/07/2026
Hora: 14:35
Usuario: Juan Pérez
```

---

## 6. Posibles extensiones futuras

### Añadir más campos a monitorizar

1. Añadir el nombre del campo en la condición `if "project_status" in vals` (o crear una lista de campos monitorizados).
2. Capturar valores anteriores para cada campo en el diccionario `old_statuses`.
3. Construir el mensaje con la información de todos los campos cambiados.

### Registrar solo ciertos cambios de estado

Filtrar por estados específicos antes de publicar:

```python
ESTADOS_A_REGISTRAR = ["pending", "in_progress", "complete"]
if new_status.xml_id.split(".")[-1] in ESTADOS_A_REGISTRAR:
    project.message_post(body=body)
```

### Añadir campos al mensaje

Para incluir campos adicionales del proyecto (ej. responsable, cliente):

```python
body = _(
    "Cambio de estado del proyecto:<br/>"
    "De <strong>%(old)s</strong> a <strong>%(new)s</strong><br/>"
    "Fecha: %(date)s<br/>"
    "Hora: %(time)s<br/>"
    "Usuario: %(user)s<br/>"
    "Proyecto: %(project)s<br/>"
    "Cliente: %(partner)s"
) % {
    # ...
    "project": project.name,
    "partner": project.partner_id.name or _("Sin cliente"),
}
```

---

## 7. Historial de cambios

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 15.0.1.0.0 | 2026-07-07 | Versión inicial: registro de cambios de `project_status` en el chatter |
