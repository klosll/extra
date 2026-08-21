# KLO — Report Layout Small Font Header

## Identificación del módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_layout_small_font_header` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Accounting/Accounting |
| **Dependencias** | `account` |
| **Ubicación** | `/opt/odoo18_desarrollo/odoo/extra-addons/klo/extra/klo_report_layout_small_font_header/` |

---

## Descripción funcional

Reduce el tamaño de fuente de la **cabecera** de los informes QWeb para lograr impresiones más compactas. Se auto-crea un parámetro de sistema `klo.report_layout_small_font_header` con valor por defecto `12`, que se inyecta como CSS en la plantilla `web.minimal_layout` (el esqueleto mínimo que envuelve todos los informes). El tamaño es configurable desde Ajustes › Técnico › Parámetros del sistema sin tocar código.

---

## Lógica (sin campos ni métodos Python)

El módulo **no añade campos ni métodos Python**. Toda la lógica reside en:

1. **Parámetro de sistema** (`data/ir_config_parameter_data.xml`): crea el registro `ir.config_parameter` con clave `klo.report_layout_small_font_header` y valor `12`. Se declara `noupdate="1"` y `forcecreate="False"` para no sobrescribir el valor si el usuario lo ha modificado manualmente.
2. **Inyección CSS** (`views/report_assets.xml`): la plantilla `klo_minimal_layout_small_font_header` hereda `web.minimal_layout` y, dentro de `<head>`, lee el parámetro de sistema y genera un `<style>` que aplica `font-size` a la clase `.header`.

### Snippet de la inyección

```xml
<t t-set="header_font_size"
   t-value="request.env['ir.config_parameter'].sudo().get_param('klo.report_layout_small_font_header', '12')"/>
<style>
    .header {
        font-size: <t t-out="header_font_size"/>px !important;
    }
</style>
```

El valor por defecto `'12'` se usa si el parámetro no existe.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `account` | Dependencia declarada (contexto de informes contables); la plantilla heredada `web.minimal_layout` pertenece al núcleo `web` |

No depende de módulos externos fuera del núcleo.

---

## Vistas / Plantillas modificadas

### Inyección CSS en el layout mínimo de informes

| Atributo | Valor |
|---|---|
| **Plantilla heredada** | `web.minimal_layout` |
| **XPath** | `//head` posición `inside` |
| **Cambio** | Lee `ir.config_parameter` `klo.report_layout_small_font_header` y añade un `<style>` con `.header { font-size: <valor>px !important; }` |

### Parámetro de sistema (datos)

| Registro | Modelo | Detalle |
|---|---|---|
| `config_param_minimal_layout_small_font_header` | `ir.config_parameter` | `noupdate="1"`, `forcecreate="False"`. Clave `klo.report_layout_small_font_header`, valor `12`. |

---

## Estructura de archivos

```
klo_report_layout_small_font_header/
├── __init__.py                          ← Importa models (vacío)
├── __manifest__.py
├── data/
│   └── ir_config_parameter_data.xml      ← Parámetro de sistema (valor 12)
├── models/
│   └── __init__.py                       ← Vacío (sin modelos)
├── views/
│   └── report_assets.xml                 ← Hereda web.minimal_layout, inyecta CSS
└── static/description/
    ├── icon.png
    └── Technical_context.md
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -i klo_report_layout_small_font_header --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d myv_dev -u klo_report_layout_small_font_header --stop-after-init
```

> La BD `myv_dev` es la definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Ampliar el CSS para reducir también el tamaño de fuente del cuerpo del informe, no solo la cabecera.
- Añadir un campo en `res.company` para configurar el tamaño de fuente por empresa en lugar de un parámetro global.
- Crear un grupo de seguridad para que solo administradores puedan modificar el parámetro de sistema.
