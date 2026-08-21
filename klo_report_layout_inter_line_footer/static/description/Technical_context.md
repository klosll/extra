# KLO — Report Layout Inter Line Footer

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_layout_inter_line_footer` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_layout_inter_line_footer/` |

---

## Descripción funcional

Permite controlar el **interlineado del pie (`line-height`) de los informes** mediante un parámetro de sistema, para conseguir una impresión más compacta. Se auto-crea el parámetro `klo.report_layout_inter_line_footer` con valor `1.0` por defecto:

- `1.0` = sin espacio adicional entre líneas
- `1.2` = 20% de espacio adicional (recomendado)
- `1.5` = 50% de espacio adicional

El usuario puede ajustar el valor desde *Ajustes › Técnico › Parámetros del sistema* sin tocar código.

---

## Campo(s) añadido(s) o lógica

No añade campos ni métodos Python. La lógica es puramente declarativa (XML + QWeb):

1. **Data XML** crea el `ir.config_parameter` con clave `klo.report_layout_inter_line_footer` y valor `1.0` (`noupdate="1"`, `forcecreate="False"` para no sobrescribir un valor editado manualmente).
2. **Template QWeb** lee el parámetro en tiempo de render y lo inyecta como `line-height` de `.o_footer_content`.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` | Dependencia base para disponer del layout de informes contables. |

No depende de módulos OCA ni externos.

---

## Vistas modificadas

### Template `web.minimal_layout`

| Vista base heredada | XPath | Acción |
|---|---|---|
| `web.minimal_layout` (template `klo_minimal_layout_small_font_footer`) | `//head` `position="inside"` | Lee el parámetro `klo.report_layout_inter_line_footer` (fallback `'1.0'`) e inyecta un `<style>` con `line-height: <valor> !important` sobre `.o_footer_content`. |

---

## Estructura de archivos

```
klo_report_layout_inter_line_footer/
├── __init__.py
├── __manifest__.py
├── data/
│   └── ir_config_parameter_data.xml   ← Crea klo.report_layout_inter_line_footer = 1.0
├── models/
│   └── __init__.py                    ← Vacío (sin modelos)
├── views/
│   └── report_assets.xml              ← Hereda web.minimal_layout
└── static/description/
    ├── icon.png
    └── Technical_context.md          ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_layout_inter_line_footer --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_layout_inter_line_footer --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Ampliar el control de interlineado al cuerpo del informe, no solo al pie.
- Exponer el valor del parámetro en un campo de configuración de `res.config.settings` para editarlo desde la UI sin ir a Parámetros del sistema.
- Aplicar el `line-height` de forma selectiva según el tipo de informe.
