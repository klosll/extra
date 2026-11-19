# KLO — Compra: cabecera con fuente pequeña

## Identificación del módulo

| Campo | Valor |
|---|---|---|
| **Nombre técnico** | `klo_purchase_report_layout_small_font_header` |
| **Versión** | 18.0.0.1.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Purchase |
| **Dependencias** | `purchase` |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_purchase_report_layout_small_font_header/` |

---

## Descripción funcional

Reduce el tamaño de fuente de la **cabecera** de los informes de compra (Pedido de compra y Solicitud de presupuesto) para lograr impresiones más compactas. Se crea un parámetro de sistema independiente `klo.report_layout_small_font_header_purchase` con valor por defecto `12`, que se inyecta como CSS en ambas plantillas de compra. El tamaño es configurable desde Ajustes › Técnico › Parámetros del sistema sin tocar código, de forma independiente al parámetro de venta.

---

## Lógica (sin campos ni métodos Python)

El módulo **no añade campos ni métodos Python**. Toda la lógica reside en:

1. **Parámetro de sistema** (`data/ir_config_parameter_data.xml`): crea el registro `ir.config_parameter` con clave `klo.report_layout_small_font_header_purchase` y valor `12`. Se declara `noupdate="1"` y `forcecreate="False"` para no sobrescribir el valor si el usuario lo ha modificado manualmente.
2. **Inyección CSS** (`views/report_assets.xml`): dos plantillas heredan los informes de compra (`purchase.report_purchaseorder_document` y `purchase.report_purchasequotation_document`) y, dentro del `<div class="page">`, leen el parámetro de sistema y generan un `<style>` que aplica `font-size` a la clase `.header` y a todos sus descendientes.

### Snippet de la inyección

```xml
<t t-set="purchase_header_font_size"
   t-value="env['ir.config_parameter'].sudo().get_param('klo.report_layout_small_font_header_purchase', '12')"/>
<style>
    .header, .header * { font-size: <t t-out="purchase_header_font_size"/>px !important; }
</style>
```

El descendiente `.header *` fuerza la sobrescritura de posibles `font-size` inline que pueda tener la cabecera compacta. El valor por defecto `'12'` se usa si el parámetro no existe.

---

## Dependencias

| Módulo | Propósito |
|---|---|---|
| `purchase` | Proporciona las plantillas de Pedido de compra y Solicitud de presupuesto que se heredan |

No depende de módulos externos fuera del núcleo.

---

## Vistas / Plantillas modificadas

### Inyección CSS en el informe de pedido de compra

| Atributo | Valor |
|---|---|---|
| **Plantilla heredada** | `purchase.report_purchaseorder_document` |
| **ID de la herencia** | `klo_purchase_order_small_font_header` |
| **XPath** | `//div[@class='page']` posición `inside` |
| **Cambio** | Lee `ir.config_parameter` `klo.report_layout_small_font_header_purchase` y añade un `<style>` con `.header, .header * { font-size: <valor>px !important; }` |

### Inyección CSS en el informe de solicitud de presupuesto

| Atributo | Valor |
|---|---|---|
| **Plantilla heredada** | `purchase.report_purchasequotation_document` |
| **ID de la herencia** | `klo_purchase_quotation_small_font_header` |
| **XPath** | `//div[@class='page']` posición `inside` |
| **Cambio** | Lee `ir.config_parameter` `klo.report_layout_small_font_header_purchase` y añade un `<style>` con `.header, .header * { font-size: <valor>px !important; }` |

### Parámetro de sistema (datos)

| Registro | Modelo | Detalle |
|---|---|---|
| `config_param_purchase_small_font_header` | `ir.config_parameter` | `noupdate="1"`, `forcecreate="False"`. Clave `klo.report_layout_small_font_header_purchase`, valor `12`. |

---

## Estructura de archivos

```
klo_purchase_report_layout_small_font_header/
├── __init__.py                          ← Importa models (vacío)
├── __manifest__.py
├── data/
│   └── ir_config_parameter_data.xml      ← Parámetro de sistema (valor 12)
├── models/
│   └── __init__.py                       ← Vacío (sin modelos)
├── views/
│   └── report_assets.xml                 ← Hereda los informes de compra, inyecta CSS
├── static/description/
│   ├── icon.png
│   └── Technical_context.md
└── .gitignore
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <base_de_datos> -i klo_purchase_report_layout_small_font_header --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <base_de_datos> -u klo_purchase_report_layout_small_font_header --stop-after-init
```

> Sustituir `<base_de_datos>` por la BD de desarrollo definida en `db_name` de `config/odoo.conf`.

---

## Posibles adaptaciones futuras

- Ampliar el CSS para reducir también el tamaño de fuente del cuerpo del informe de compra, no solo la cabecera.
- Añadir un campo en `res.company` para configurar el tamaño de fuente por empresa en lugar de un parámetro global.
- Crear un grupo de seguridad para que solo administradores puedan modificar el parámetro de sistema.
