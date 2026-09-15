# Technical Context — `klo_report_saleorder_no_salesperson`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_saleorder_no_salesperson` |
| **Nombre legible** | KLO - Informe de pedido de venta sin comercial en cabecera |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales/Sales |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_report_saleorder_no_salesperson/` |

---

## Descripción

El informe de pedido de venta estándar de Odoo (`sale.report_saleorder_document`) muestra en la cabecera un bloque con el campo **Salesperson** (`doc.user_id.name`), que es el comercial asignado al pedido.

Este módulo **oculta ese bloque** para que el comercial no aparezca en la cabecera del PDF del pedido de venta. No modifica el modelo de datos ni añade campos: actúa exclusivamente sobre el template QWeb del informe.

---

## Campo(s) añadido(s)

No aplica. El módulo no añade ni modifica campos de ningún modelo.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` (núcleo Odoo) | Provee el template QWeb `sale.report_saleorder_document` que este módulo hereda |

---

## Lógica

No hay lógica Python. El módulo es puramente declarativo (XML):

- Se hereda el template `sale.report_saleorder_document`.
- Mediante un `xpath` se localiza el `div` que contiene el bloque Salesperson y se desactiva su condición `t-if` poniéndola a `False`, de modo que el bloque no se renderiza en el informe.

La vista padre define el bloque así (en `addons/sale/report/ir_actions_report_templates.xml`):

```xml
<div t-if="doc.user_id.name" class="col">
    <strong>Salesperson</strong>
    <div t-field="doc.user_id">Mitchell Admin</div>
</div>
```

> **Nota importante**: el `xpath` debe apuntar al elemento `div` (no a `t`), porque la condición `t-if` vive en el `div`. Un `xpath` como `//t[@t-if="doc.user_id.name"]` no localiza nada y rompe la carga del módulo.

---

## Vistas modificadas

### Template QWeb `sale.report_saleorder_document` — informe de pedido de venta

**Archivo:** `reports/report_saleorder_document.xml`
**ID template:** `klo_report_saleorder_document_no_salesperson`
**Hereda:** `sale.report_saleorder_document`

#### XPath aplicado

```xml
<xpath expr='//div[@t-if="doc.user_id.name"]' position="attributes">
    <attribute name="t-if">False</attribute>
</xpath>
```

**Motivo del cambio:** ocultar el bloque "Salesperson" de la cabecera del informe de pedido de venta. Se elige desactivar el `t-if` (en lugar de `position="replace"`) porque es la técnica menos invasiva: mantiene el resto del template intacto y es fácil de revertir si el cliente quiere volver a mostrar el comercial.

---

## Estructura de archivos

```
klo_report_saleorder_no_salesperson/
├── __init__.py
├── __manifest__.py
├── reports/
│   └── report_saleorder_document.xml   ← Herencia del template QWeb del informe
└── static/description/
    ├── icon.png
    └── Technical_context.md            ← Este fichero
```

---

## Instalación / Actualización

```bash
# Instalar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <nombre_base_datos> -i klo_report_saleorder_no_salesperson --stop-after-init

# Actualizar
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <nombre_base_datos> -u klo_report_saleorder_no_salesperson --stop-after-init
```

> El nombre de la base de datos se lee siempre de `db_name` en `config/odoo.conf`; no está hardcodeado.

---

## Comportamiento esperado

| Situación | Resultado |
|---|---|
| Imprimir un pedido de venta (PDF) | La cabecera NO muestra el bloque "Salesperson" |
| El pedido tiene comercial asignado (`user_id`) | El comercial no aparece en el informe |
| El pedido no tiene comercial asignado | El bloque ya no se renderizaba por el `t-if` original; sin cambios |

---

## Posibles adaptaciones futuras

- **Mostrar el comercial solo en ciertos estados:** en lugar de `False` fijo, el `t-if` podría condicionarse (p. ej. `doc.state in ['draft', 'sent']`) para mostrar el comercial solo en presupuestos.
- **Ocultar otros campos de la cabecera:** el mismo patrón de `xpath` + `attribute t-if=False` puede aplicarse a otros bloques del informe (referencia, fecha, validez, etc.).
- **Hacerlo configurable:** añadir un parámetro de sistema (`ir.config_parameter`) que permita activar/desactivar la visibilidad del comercial sin tocar el código.