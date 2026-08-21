# KLO — Res Partner Parent ID Numérico

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_res_partner_parent_id_numeric` |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Extra Tools |
| **Dependencias** | `base` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_res_partner_parent_id_numeric/` |

---

## Descripción funcional

Muestra el **ID numérico de la empresa padre** (`parent_id`) en la ficha de contacto de `res.partner`. Resulta útil para identificar de forma rápida, mediante el identificador interno de Odoo, a qué empresa está vinculada una dirección/ contacto hijo, sin necesidad de abrir el formulario de la empresa padre.

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

**Lógica del compute** (`@api.depends("parent_id")`):
```python
partner.parent_id_numeric = partner.parent_id.id if partner.parent_id else 0
```
Devuelve el `.id` del `parent_id` o `0` si el contacto no tiene empresa padre.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `base` | Provee el modelo `res.partner` y la vista `base.view_partner_form` que se hereda. |

No depende de módulos OCA ni externos.

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

- Convertir el campo en `store=True` para permitir búsquedas/filtrados por ID de empresa padre en vistas lista y filtros de búsqueda.
- Mostrar también el ID numérico del propio contacto (no solo el del padre) en la misma vista.
- Añadir el campo en la vista lista de contactos como columna opcional.
