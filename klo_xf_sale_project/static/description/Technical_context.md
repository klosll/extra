# KLO - Proyectos de venta y analítica

## Módulo

| Campo | Valor |
|---|---|
| Nombre técnico | `klo_xf_sale_project` |
| Versión | `18.0.1.2.0` |
| Autor | KLO Ingeniería Informática S.L.L. |
| Licencia | AGPL-3 |
| Ruta | `extra-addons/klo/extra/klo_xf_sale_project` |

## Descripción

Amplía `xf_sale_project` con ajustes KLO de ventas y proyectos. Integra las validaciones
analíticas que antes proporcionaba `klo_analytic_v14_compat`: una sola cuenta al 100% por
línea y selección manual obligatoria de cuenta analítica en proyectos. Las reglas de
visibilidad de planes y prefijos contables se configuran manualmente en Odoo.

La cuenta analítica del proyecto no se copia del usuario responsable ni se crea
automáticamente.

## Campo(s) añadido(s)

No añade campos persistentes nuevos en esta integración. Hace obligatorio el campo
existente `project.project.account_id`.

## Dependencias

* `account` y `project` de Odoo.
* `xf_sale_project`, módulo de proyectos de venta del que parte esta personalización.

## Lógica

* `models/project.py`: exige cuenta analítica al crear un proyecto, impide quitarla y
  bloquea su creación automática. Mantiene el resto de ajustes KLO del módulo.
* `models/analytic_mixin.py`: permite guardar una sola cuenta analítica al 100% en cada
  distribución.
* `klo_klo/models/project_project.py`: se han retirado las asignaciones que copiaban al
  proyecto la cuenta analítica del usuario/gerente.

## Vistas modificadas

`views/project.xml` hereda `project.edit_project` y marca la cuenta analítica como
obligatoria.

## Estructura de archivos

```text
klo_xf_sale_project/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── analytic_mixin.py
│   └── project.py
├── views/project.xml
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

## Instalación / Actualización

```bash
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d <base_activa> -u klo_xf_sale_project --stop-after-init
```

## Posibles adaptaciones futuras

Si se desea permitir repartos analíticos, cambiar `_check_single_analytic_account`.
Si se desea permitir proyectos sin cuenta o creación automática, revisar los métodos
añadidos a `project.project`.
