# Technical Document — klo_website_basic_customer_portal

**Versión:** 15.0.1.0.0  
**Autor:** KLO Ingeniería Informática S.L.L.  
**Licencia:** AGPL-3  
**Categoría:** Website / Portal  
**Ruta:** `extra-addons/klo/extra/klo_website_basic_customer_portal/`

---

## 1. Propósito

Este módulo limita las secciones visibles en la página **"Mi Cuenta"** del portal de cliente (`/my/home`) para mostrar únicamente las entradas relevantes para los clientes finales de KLO:

| Visible | Módulo origen |
|---------|--------------|
| ✅ Presupuestos | `sale` |
| ✅ Pedidos de venta | `sale` |
| ✅ Facturas | `account` |

El resto de secciones que Odoo muestra por defecto quedan ocultas:

| Oculto | XML ID desactivado | Módulo origen |
|--------|--------------------|--------------|
| Solicitudes de presupuesto de compra + Pedidos de compra | `purchase.portal_my_home_purchase` | `purchase` |
| Proyectos y Tareas | `project.portal_my_home` | `project` |
| Partes de horas | `hr_timesheet.portal_my_home_timesheet` | `hr_timesheet` |
| Contratos | `contract.portal_my_home_contract` | `contract` (OCA) |

---

## 2. Estructura de ficheros

```
klo_website_basic_customer_portal/
├── __manifest__.py              # Metadatos, dependencias, uninstall_hook
├── __init__.py                  # Importa uninstall_hook para exponerlo al módulo raíz
├── hooks.py                     # Lógica del uninstall_hook
├── views/
│   └── portal_templates.xml    # Desactiva las vistas de portal no deseadas
└── static/
    └── description/
        ├── icon.png             # Icono del módulo (copiado de klo_klo)
        └── Technical_document.md  # Este fichero
```

---

## 3. Mecanismo técnico

### 3.1 Cómo se ocultan las secciones

Odoo construye la página `/my/home` a partir de la plantilla base `portal.portal_my_home`. Cada módulo instalado que quiere añadir entradas hereda esa plantilla con una vista QWeb propia (atributo `customize_show="True"`).

La estrategia del módulo **no usa herencia de vistas** sino que **desactiva directamente** los registros `ir.ui.view` de los módulos de terceros poniendo `active=False` mediante registros `<record>` en el XML de datos:

```xml
<record id="purchase.portal_my_home_purchase" model="ir.ui.view">
    <field name="active" eval="False"/>
</record>
```

Esto es suficiente porque Odoo solo renderiza vistas con `active=True`.

### 3.2 Por qué se necesita uninstall_hook

Cuando Odoo desinstala un módulo, **no revierte automáticamente** los cambios que ese módulo hizo sobre registros de otros módulos (el `active=False` queda persistido en la BD). Para restaurar el comportamiento original al desinstalar, se declara un `uninstall_hook` en el manifiesto:

```python
# __manifest__.py
'uninstall_hook': 'uninstall_hook',
```

Odoo llama a esta función justo antes de eliminar los datos del módulo, permitiendo reactivar las vistas:

```python
# hooks.py
def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xml_id in VIEWS_TO_RESTORE:
        view = env.ref(xml_id, raise_if_not_found=False)
        if view:
            view.active = True
```

### 3.3 Cómo exponer el hook a Odoo

Odoo busca el `uninstall_hook` como atributo directo del módulo Python raíz (`odoo.addons.klo_website_basic_customer_portal`). Por eso en `__init__.py` se importa la función explícitamente, **no** el módulo `hooks`:

```python
# CORRECTO
from .hooks import uninstall_hook

# INCORRECTO — Odoo no encontraría el atributo
from . import hooks
```

---

## 4. Dependencias

| Módulo | Razón |
|--------|-------|
| `portal` | Plantilla base `portal.portal_my_home` |
| `sale` | Vistas de Presupuestos y Pedidos de venta (se mantienen visibles) |
| `account` | Vista de Facturas (se mantiene visible) |
| `purchase` | Vista que se desactiva: `portal_my_home_purchase` |
| `project` | Vista que se desactiva: `portal_my_home` |
| `hr_timesheet` | Vista que se desactiva: `portal_my_home_timesheet` |
| `contract` | Vista que se desactiva: `portal_my_home_contract` (módulo OCA) |

---

## 5. Instalación y desinstalación

```bash
# Instalar
/opt/odoo15_klo/venv/bin/python /opt/odoo15_klo/odoo/odoo-bin \
  -c /opt/odoo15_klo/odoo/config/odoo15.conf \
  -i klo_website_basic_customer_portal --stop-after-init
```

**Desinstalación recomendada:** desde la interfaz web (Ajustes → Aplicaciones) o con el shell de Odoo:

```python
# odoo-bin shell
module = env['ir.module.module'].search([('name', '=', 'klo_website_basic_customer_portal')])
module.button_immediate_uninstall()
```

> ⚠️ **No usar** `UPDATE ir_module_module SET state='to remove'` directamente en la BD y luego `-u <modulo>` sobre el mismo módulo: Odoo restaura el estado a `installed` sin procesar la eliminación. Si se marca manualmente como `to remove`, hay que disparar el ciclo de actualización con un módulo diferente o usar el shell.

---

## 6. Posibles extensiones futuras

### Añadir más vistas a ocultar

1. Localizar el XML ID de la vista heredada de `portal.portal_my_home` del módulo en cuestión.
2. Añadir en `views/portal_templates.xml`:
   ```xml
   <record id="<modulo>.<xml_id>" model="ir.ui.view">
       <field name="active" eval="False"/>
   </record>
   ```
3. Añadir el mismo XML ID a `VIEWS_TO_RESTORE` en `hooks.py`.
4. Añadir el módulo a `depends` en `__manifest__.py`.
5. Actualizar el módulo: `-u klo_website_basic_customer_portal --stop-after-init`.

### Ver qué módulos aportan entradas al portal

```bash
grep -rn 'inherit_id="portal.portal_my_home"' \
  /opt/odoo15_klo/odoo/addons/ \
  /opt/odoo15_klo/odoo/extra-addons/ \
  --include="*.xml"
```

---

## 7. Historial de cambios

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 15.0.1.0.0 | 2026-06-26 | Versión inicial: oculta purchase, project, hr_timesheet, contract del portal |
