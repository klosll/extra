# Technical Context — `klo_report_saleorder_replace_date_order_by_commitment_date`

## Módulo

| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_report_saleorder_replace_date_order_by_commitment_date` |
| **Nombre legible** | KLO - Informe de pedido de venta: fecha de pedido por fecha de compromiso |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Categoría** | Sales/Sales |
| **Ubicación** | `extra-addons/klo/extra/klo_report_saleorder_replace_date_order_by_commitment_date/` |

---

## Descripción

El informe de pedido de venta estándar de Odoo (`sale.report_saleorder_document`) muestra en la cabecera un bloque con la fecha del pedido (`doc.date_order`), cuya etiqueta varía según el estado (Quotation Date / Order Date / Issued Date).

Este módulo **reemplaza la fecha mostrada** en ese bloque: en lugar de `doc.date_order` (fecha en que se creó/modificó el pedido) muestra **`doc.commitment_date`** (fecha de entrega comprometida con el cliente). No modifica el modelo de datos ni añade campos: actúa exclusivamente sobre el template QWeb del informe mediante herencia XML con `position="attributes"`.

---

## Campo(s) añadido(s)

**Ninguno.** Este módulo es puramente declarativo (herencia QWeb). No añade ni modifica campos de ningún modelo Python.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `sale` (núcleo Odoo) | Provee el template QWeb `sale.report_saleorder_document` que este módulo hereda |

---

## Lógica

No hay lógica Python. El módulo es puramente declarativo (XML):

- Se hereda el template `sale.report_saleorder_document`.
- Mediante un `xpath` se localiza el `div` hijo con `t-field="doc.date_order"` dentro del `div` padre `name="informations_date"` y se cambia su atributo `t-field` a `doc.commitment_date`.

El template padre define el bloque así (en `addons/sale/report/ir_actions_report_templates.xml`, líneas 52-57):

```xml
<div t-if="doc.date_order" class="col" name="informations_date">
    <strong t-if="is_proforma">Issued Date</strong>
    <strong t-elif="doc.state in ['draft', 'sent']">Quotation Date</strong>
    <strong t-else="">Order Date</strong>
    <div t-field="doc.date_order" t-options='{"widget": "date"}'>2023-12-31</div>
</div>
```

> **Nota importante sobre la preservación de `<strong>` y `t-if`:** El `xpath` apunta **únicamente** al `div` con `t-field="doc.date_order"` (position="attributes"), sin tocar el `div` padre ni los `<strong>`. Esto es intencional: los `<strong>` contienen las etiquetas traducibles ("Quotation Date" / "Order Date" / "Issued Date") y sus condiciones `t-if`/`t-elif`/`t-else` dependen del estado del pedido. Si el `xpath` sustituyera el `div` padre completo (`position="replace"`), habría que reescribir toda la lógica de etiquetas y rompería las traducciones existentes. El enfoque de `position="attributes"` es el menos invasivo posible.

> **Sobre la condición `t-if` del div padre:** El `div` padre tiene `t-if="doc.date_order"`. Si `commitment_date` está vacío, el `div` padre se renderizará igualmente (porque `date_order` tiene valor), mostrando la etiqueta (Quotation Date/Order Date) con el valor vacío del campo `commitment_date`. Ver "Posibles adaptaciones futuras" si se necesita ocultar el bloque cuando `commitment_date` esté vacío.

---

## Vistas modificadas

### Template QWeb `sale.report_saleorder_document` — informe de pedido de venta

**Archivo:** `reports/report_saleorder_document.xml`
**ID template:** `klo_report_saleorder_document_date_order_by_commitment_date`
**Hereda:** `sale.report_saleorder_document`

#### XPath aplicado

```xml
<xpath expr="//div[@name='informations_date']/div[@t-field='doc.date_order']" position="attributes">
    <attribute name="t-field">doc.commitment_date</attribute>
</xpath>
```

**Motivo del cambio:** reemplazar la fecha del pedido (`date_order`) por la fecha de compromiso (`commitment_date`) en la cabecera del informe PDF, para que el cliente vea la fecha de entrega acordada en lugar de la fecha de emisión del pedido. Se elige `position="attributes"` para modificar solo el atributo `t-field` sin reemplazar el nodo, preservando así los `<strong>` con sus condiciones de traducción y el `t-options='{"widget": "date"}'` original.

---

## Estructura de archivos

```
klo_report_saleorder_replace_date_order_by_commitment_date/
├── __init__.py                          ← Vacío (sin modelos Python)
├── __manifest__.py                      ← Metadatos del módulo
├── reports/
│   └── report_saleorder_document.xml    ← Herencia del template QWeb del informe
└── static/description/
    ├── icon.png                         ← Icono del módulo
    └── Technical_context.md             ← Este fichero
```

---

## Comportamiento esperado

| Situación | Resultado |
|---|---|
| Imprimir un pedido de venta (PDF) | La cabecera muestra la **fecha de compromiso** (`commitment_date`) en lugar de la fecha del pedido |
| El pedido tiene `commitment_date` definida | Se muestra esa fecha bajo la etiqueta correspondiente (Quotation Date / Order Date / Issued Date) |
| El pedido **no** tiene `commitment_date` definida | El `div` padre se renderiza igualmente (porque `date_order` tiene valor), mostrando la etiqueta con el valor vacío |
| El pedido no tiene `date_order` | El `div` padre no se renderiza (condición `t-if="doc.date_order"`) — sin cambios respecto al comportamiento estándar |

---

## Instalación / Actualización

```bash
# Instalar
/opt/odoo18_desarrollo/uv/.venv/bin/python /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <db_name> -i klo_report_saleorder_replace_date_order_by_commitment_date --stop-after-init

# Actualizar
/opt/odoo18_desarrollo/uv/.venv/bin/python /opt/odoo18_desarrollo/odoo/odoo-bin \
  -c /opt/odoo18_desarrollo/config/odoo.conf \
  -d <db_name> -u klo_report_saleorder_replace_date_order_by_commitment_date --stop-after-init
```

Alternativa con `uv run`:

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <db_name> -u klo_report_saleorder_replace_date_order_by_commitment_date --stop-after-init
```

> El nombre de la base de datos (`<db_name>`) se lee siempre de `db_name` en `config/odoo.conf`; no está hardcodeado.

---

## Posibles adaptaciones futuras

- **Ocultar el bloque cuando `commitment_date` esté vacío:** cambiar el `t-if` del `div` padre `name="informations_date"` a `doc.commitment_date` (en lugar de `doc.date_order`) para que no se renderice cuando no hay fecha de compromiso. Esto requeriría un segundo `xpath`:
  ```xml
  <xpath expr="//div[@name='informations_date']" position="attributes">
      <attribute name="t-if">doc.commitment_date</attribute>
  </xpath>
  ```
  **Atención:** esto ocultaría el bloque completo incluyendo la etiqueta, y si `date_order` sigue teniendo valor, el pedido no mostraría ninguna fecha.

- **Personalizar la etiqueta `<strong>`:** si se desea cambiar "Quotation Date" / "Order Date" / "Issued Date" por una etiqueta fija (p. ej. "Fecha de entrega"), se puede heredar el `<strong>` con `position="replace"` y definir una etiqueta única. Esto sí afectaría las traducciones del template padre.

- **Usar otro campo:** el mismo patrón de `xpath` + `position="attributes"` puede aplicarse para mostrar cualquier otro campo de tipo fecha de `sale.order` (p. ej. `create_date`, un campo `x_` personalizado, etc.).

- **Añadir el campo de fecha original como columna adicional:** en lugar de reemplazar, duplicar el bloque mostrando ambas fechas (pedido y compromiso) como dos columnas separadas en la cabecera.
