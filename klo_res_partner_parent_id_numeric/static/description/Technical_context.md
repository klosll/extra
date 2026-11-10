# KLO — Res Partner Parent ID Numérico

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_res_partner_parent_id_numeric` |
| **Versión** | 18.0.1.0.2 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Extra Tools |
| **Dependencias** | `base` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_res_partner_parent_id_numeric/` |

---

## Descripción funcional

Muestra el **ID numérico de la empresa** en la ficha de contacto de `res.partner`. El valor se resuelve en una única regla:

- Si el contacto **tiene empresa padre** (`parent_id` informado), se muestra el **ID de esa empresa padre**.
- Si el contacto **no tiene empresa padre**, se muestra su **propio ID**.

En la práctica, las compañías estándar de Odoo no suelen tener `parent_id`, por lo que mostrarán su propio ID; los contactos/direcciones vinculados a una empresa mostrarán el ID de dicha empresa. Resulta útil para identificar de forma rápida, mediante el identificador interno de Odoo, a qué empresa está vinculada una dirección/contacto hijo —o qué ID tiene la propia compañía— sin necesidad de abrir el formulario de la empresa padre.

---

## Campo(s) añadido(s)

| Atributo | Valor |
|---|---|
| **Modelo** | `res.partner` (vía `_inherit`) |
| **Nombre técnico** | `parent_id_numeric` |
| **Tipo** | `Integer` |
| **String** | `ID Empresa` |
| **compute** | `_compute_parent_id_numeric` |
| **store** | `False` (no persistente, calculado en vivo) |

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `base` | Provee el modelo `res.partner` y la vista `base.view_partner_form` que se hereda. |

No depende de módulos OCA ni externos.

---

## Lógica

El campo `parent_id_numeric` es calculado (no persistente) mediante `_compute_parent_id_numeric`, disparado con `@api.depends("parent_id")`.

```python
@api.depends("parent_id")
def _compute_parent_id_numeric(self):
    for partner in self:
        # Empresa padre si existe; en caso contrario, el propio ID del contacto
        partner.parent_id_numeric = partner.parent_id.id if partner.parent_id else partner.id or 0
```

| Caso | Valor mostrado |
|---|---|
| Contacto que **tiene empresa padre** | `parent_id.id` |
| Contacto que **no tiene empresa padre** | `partner.id` (su propio ID) |

`is_company` no figura en los `@api.depends` porque el resultado no depende del tipo de contacto, sino únicamente de si existe `parent_id`: las compañías estándar no suelen tener `parent_id`, por lo que muestran su propio ID.

---

## Vistas modificadas

### Formulario de contacto (`res.partner`)

| Vista base heredada | XPath | Acción |
|---|---|---|
| `base.view_partner_form` | `//h1` `position="after"` | Añade el campo `parent_id_numeric` como `readonly="1"`, justo debajo del título del contacto. |

---

## Estructura de archivos

```
klo_res_partner_parent_id_numeric/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_partner.py          ← Añade parent_id_numeric (compute)
├── views/
│   └── res_partner_views.xml   ← Hereda base.view_partner_form
└── static/description/
    ├── icon.png
    └── Technical_context.md    ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_res_partner_parent_id_numeric --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_res_partner_parent_id_numeric --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Convertir el campo en `store=True` para permitir búsquedas/filtrados por ID de empresa en vistas lista y filtros de búsqueda.
- Añadir el campo en la vista lista de contactos como columna opcional.
- **Compañías subsidiarias**: una compañía que tenga empresa matriz (subsidiaria con `parent_id` informado) mostrará el **ID de la matriz** (`parent_id.id`), no su propio ID, porque la regla actual prioriza la existencia de `parent_id`. Si en el futuro se necesitara mostrar el ID propio de la subsidiaria en este campo, habría que revisar la expresión; de lo contrario, para no alterar `parent_id_numeric` (ya consumido desde informes/exportaciones), lo correcto sería añadir un segundo campo (p. ej. `parent_company_id_numeric`).
