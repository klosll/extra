# Tecnical_document.md — klo_report_stockpicking_project

## Descripción general

Módulo KLO para Odoo 18 Community que hereda el informe QWeb de **Entrega a cliente** (`stock.report_delivery_document`) y añade el campo **Proyecto** (`project_id`) en la cabecera del documento impreso, a la derecha del campo **Pedido** (`origin`).

---

## Datos del módulo

| Atributo        | Valor                                              |
|-----------------|----------------------------------------------------|
| Nombre técnico  | `klo_report_stockpicking_project`                  |
| Versión         | 18.0.1.0.0                                         |
| Categoría       | Stock / Informes                                    |
| Autor           | KLO                                                |
| Licencia        | LGPL-3                                             |
| Dependencias    | `stock`, `project`                                 |

---

## Contexto técnico

### Campo utilizado

- **Modelo**: `stock.picking`
- **Campo**: `project_id`
- **Tipo**: `Many2one` → `project.project`
- **Nota**: Este campo no pertenece al core de Odoo 18. Fue añadido a `stock.picking` por un módulo externo instalado en la base de datos `ryp_dev`.

### QWeb heredado

- **Template heredado**: `stock.report_delivery_document`
- **Fichero original**: `addons/stock/report/report_deliveryslip.xml`
- **Estrategia de herencia**: `xpath` con `position="after"` sobre `div[@name='div_origin']`

---

## Cambios realizados

### `report/report_deliveryslip_project.xml`

Hereda `stock.report_delivery_document` mediante un `<xpath>` sobre el `div` con `name="div_origin"` (campo **Pedido** / `o.origin`) e inserta a continuación un nuevo `div` con `name="div_project"` que muestra el nombre del proyecto.

```xml
<xpath expr="//div[@name='div_origin']" position="after">
    <div t-if="o.project_id" class="col col-3 mw-100 mb-2" name="div_project">
        <strong>Proyecto</strong>
        <div t-field="o.project_id" class="m-0"/>
    </div>
</xpath>
```

- El bloque se muestra **solo si `o.project_id` tiene valor** (`t-if="o.project_id"`).
- El campo `project_id` es Many2one, por lo que `t-field` muestra el nombre del proyecto.
- El `div` padre `#informations` usa `flexbox row`, de modo que el nuevo bloque queda alineado horizontalmente a la derecha de **Pedido** y a la izquierda de **Fecha de envío**.

---

## Estructura de ficheros

```
klo_report_stockpicking_project/
├── __init__.py
├── __manifest__.py
├── report/
│   └── report_deliveryslip_project.xml
└── static/
    └── description/
        ├── icon.png              ← Logo KLO
        └── Tecnical_document.md  ← Este fichero
```

---

## Notas para futuras adaptaciones

- Si se quiere mostrar también en la **entrega a proveedor** (recepción), el mismo template `stock.report_delivery_document` se usa para ambos sentidos; basta con el `t-if="o.project_id"` ya implementado.
- Si en algún momento `project_id` se mueve a otro módulo o cambia de nombre, solo hay que actualizar el xpath y el `t-field` en el XML.
- Para añadir más campos en la cabecera (p.ej. `analytic_account_id`), basta con añadir más `div` con `position="after"` en el mismo xpath o encadenar nuevos xpaths sobre `div[@name='div_project']`.
- El campo `project_id` en `stock.picking` fue detectado como `many2one → project.project` mediante consulta directa a `ir_model_fields` en `ryp_dev`.

---

## Instalación

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
  /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d ryp_dev \
  -i klo_report_stockpicking_project \
  --stop-after-init --no-http
```

