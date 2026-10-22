# KLO — Invoice Report Price Unit Untaxed

> **Documento técnico del módulo `klo_invoice_report_price_unit_untaxed`.**
> Elaborado a partir de la plantilla `klo/_templates/static/description/Tecnical_document.md`.
> Orientado a ser procesado por una IA para futuros ajustes y desarrollos.

---

## Módulo

| Campo          | Valor                                                       |
|----------------|-------------------------------------------------------------|
| name           | `klo_invoice_report_price_unit_untaxed`                     |
| version        | `18.0.2.0.0`                                                 |
| author         | KLO Ingeniería Informática S.L.L.                            |
| license        | AGPL-3                                                      |
| path           | `extra-addons/klo/extra/klo_invoice_report_price_unit_untaxed` |
| Nombre legible | KLO - Invoice Report Price Unit Untaxed                      |
| Categoría      | Accounting/Accounting                                       |
| Dependencias   | `account`                                                   |
| Fecha creación | 2026-10-20                                                  |
| Odoo versión   | 18.0 Community                                              |

---

## Descripción

Módulo de adaptación que sustituye el precio unitario mostrado en el informe de
factura, mostrando el precio **sin impuestos** en lugar del precio con IVA incluido.

Es el equivalente para factura del módulo `klo_sale_order_price_unit_untaxed`
(aplicado al informe de presupuesto/pedido de venta y a su portal).

Afecta a los siguientes puntos de la aplicación:

- Informe PDF de factura (`account.report_invoice_document`, template QWeb definido
  en `addons/account/views/report_invoice.xml`).
- Vista previa HTML del portal de facturas del cliente (`/my/invoices/<id>`): el
  controlador `account/controllers/portal.py` renderiza **este mismo template** con
  `report_type='html'` vía `_show_report`, por lo que queda cubierto sin tocar
  ninguna plantilla de portal.

El cálculo se realiza con `compute_all` de `account.tax` sobre el `price_unit` de la
línea con `quantity=ESCALA` (10000.0), tomando la clave `total_excluded` y dividiendo
entre `ESCALA` para anular el redondeo a céntimos, de modo que funciona
tanto si los impuestos están configurados como "precio incluido" como "precio excluido".

---

## Campo(s) añadido(s)

**Modelo:** `account.move.line` — herencia `_inherit`
**Archivo:** `models/account_move_line.py`

| Campo | Tipo | String | Descripción |
|-------|------|--------|-------------|
| `price_unit_untaxed` | `Float` | `Precio unitario (sin IVA)` | Precio unitario sin impuestos de la línea. No almacenado (`store=False`), `min_display_digits='Product Price'`, calculado al vuelo en el render del informe. |

---

## Dependencias

> Otros módulos `klo_*` o del proyecto de los que este módulo depende o con los que interactúa.

- `account` (Odoo core): herencia del modelo `account.move.line` y del template
  `account.report_invoice_document`. Única dependencia del manifest.
- `klo_sale_order_price_unit_untaxed`: módulo de referencia cuyo patrón replica
  este (para venta). **No** existe dependencia técnica entre ambos; son instalables
  de forma independiente.

---

## Lógica

### Método añadido: `_compute_price_unit_untaxed` (`account.move.line`)

```python
ESCALA = 10000.0


@api.depends('price_unit', 'tax_ids', 'product_id', 'currency_id', 'partner_id', 'display_type')
def _compute_price_unit_untaxed(self):
    for line in self:
        if line.display_type != 'product':
            line.price_unit_untaxed = 0.0
            continue
        if line.tax_ids:
            taxes_result = line.tax_ids.compute_all(
                line.price_unit,
                currency=line.currency_id,
                quantity=ESCALA,
                product=line.product_id,
                partner=line.partner_id,
            )
            line.price_unit_untaxed = taxes_result['total_excluded'] / ESCALA
        else:
            line.price_unit_untaxed = line.price_unit
```

- Líneas que no son de producto (`display_type != 'product'`: `line_section`,
  `line_note`, `cogs`, `payment_term`, `tax`, `discount`, `rounding`, `epd`) reciben
  `0.0` y **no** se les aplica `compute_all`: son líneas sin precio unitario de
  venta (y la mayoría sin producto), por lo que calcularles impuestos solo añade
  ruido en el registro de cómputos sin ningún uso del valor. El informe core, de
  todos modos, no renderiza la celda para estas líneas (`t-if line.display_type == 'product'`).
- Líneas de producto con impuestos → `tax_ids.compute_all(...)['total_excluded']`
  con `quantity=ESCALA`, dividiendo después entre `ESCALA`.
- Líneas de producto sin impuestos → directamente `price_unit` (ya es precio base).

**Escalado de la cantidad (`ESCALA = 10000.0`):** `compute_all` redondea SIEMPRE
los totales a la precisión de la moneda (céntimos): con `quantity=1.0` devolvería
la base unitaria ya redondeada a 2 decimales (p. ej. `1.41` en lugar de `1.416669`).
Al llamar con `quantity=ESCALA` y dividir el total entre `ESCALA`, el error de
redondeo se divide entre `ESCALA` (depende de la precisión de la moneda: con
céntimos, del orden de 5e-7; con monedas sin decimales puede ser mayor, del orden
de 5e-5), suficiente para presentar 6 decimales. La técnica es lineal para
impuestos porcentuales y de importe fijo, que se multiplican por la cantidad, por
lo que el precio unitario resultante no varía.

No se usa un API 'sin redondeo' del motor de impuestos porque Odoo 18 no expone
públicamente la base unitaria sin redondear (`compute_all` devuelve
`total_excluded` ya redondeado a la moneda; `raw_total_excluded` es interno):
escalar la cantidad evita tocar internals privados.

**Notas sobre los campos usados** (verificados contra `addons/account/models/account_move_line.py`):

- Los impuestos de la línea se llaman `tax_ids` (Many2many a `account.tax`),
  **no** `tax_id` como en `sale.order.line`.
- `partner_id` existe directamente en `account.move.line` (computado a partir de
  `move_id.partner_id.commercial_partner_id`), por lo que no hace falta bajar al move.
- `currency_id` es la moneda de la línea (coincide con la del apunte en facturas)
  y es la que usan los campos `Monetary` vecinos (`price_subtotal`, `price_total`).
- `display_type` se incluye en el `@api.depends` porque el compute ramifica según
  ese campo (líneas de producto frente al resto).

---

## Vistas modificadas

### `account.report_invoice_document` — Informe de factura (PDF y HTML de portal)

**Archivo:** `report/account_report_templates.xml`
**ID template:** `report_invoice_document_untaxed_price`
**Hereda:** `account.report_invoice_document`

#### XPath aplicado

```xml
<xpath expr="//td[@name='td_price_unit']/span" position="replace">
    <span class="text-nowrap" t-field="line.price_unit_untaxed"/>
</xpath>
```

**Motivo del cambio:** el template original muestra `line.price_unit` con `t-field`,
que en facturas con impuestos "precio incluido" lleva IVA embebido. Se sustituye el
`<span>` por uno que renderiza `line.price_unit_untaxed` con `t-field`, que toma el
formato del campo (`min_display_digits='Product Price'`): muestra los mismos
decimales que `price_unit` en el formulario y sin símbolo de moneda, del mismo
modo que renderiza el core la celda original.

**Observación de precisión:** los decimales mostrados los gobierna `t-field` a
partir del `min_display_digits='Product Price'` del campo (mismos decimales que
`price_unit` en el formulario), y el valor no lleva símbolo de moneda. Mismo
criterio que el módulo hermano `klo_sale_order_price_unit_untaxed`.

**Conservación del `<td>`:** el reemplazo se limita al `<span>` interior; el
`<td name="td_price_unit">` y su `t-attf-class` original (`text-end` +
`d-none d-md-table-cell` cuando `report_type == 'html'`) quedan intactos del
template core, imprescindibles para que la columna se oculte en móvil en la vista
previa HTML del portal, que reutiliza este mismo template. Por ese motivo **no** se
toca ninguna plantilla de portal (`portal` no se añade a `depends`).

**Unicidad del xpath:** en Odoo 18, `td[@name='td_price_unit']` aparece una sola vez
en `addons/account/views/report_invoice.xml` (líneas 152-154, cuerpo de la tabla de
líneas, dentro de `t t-if="line.display_type == 'product'"`) y contiene un único
`<span>` hijo, por lo que `//td[@name='td_price_unit']/span` coincide con un único
nodo.

**Conflicto conocido con otros módulos (leer antes de coinstalar):**

- El módulo OCA `sale_layout_category_hide_detail`
  (`extra-addons/oca/sale-reporting/sale_layout_category_hide_detail/views/invoice_report_templates.xml`)
  hereda `account.report_invoice_document` con
  `xpath expr="//span[@t-field='line.price_unit']" position="attributes"` para
  añadir un `t-if` condicionado a `current_section.show_line_amount`. Cualquier
  otro módulo que referencie `span[@t-field='line.price_unit']` está en la misma
  situación.
- Nuestro span sustituto usa `t-field="line.price_unit_untaxed"` (ya no conserva
  `t-field="line.price_unit"`): si ese módulo se aplica **después** del nuestro,
  su xpath no encuentra el nodo y se produce `ViewSynthesisError`; si se aplica
  **antes**, su `t-if` se pierde silenciosamente al reemplazarse el span.
- Para **minimizar** el conflicto, el reemplazo se limita exclusivamente al
  `<span>` interior (`//td[@name='td_price_unit']/span`): el `<td>` y su
  `t-attf-class` quedan intactos, por lo que cualquier herencia de terceros
  dirigida al `<td>` (atributos, clases, `before`/`after`/`inside`) sigue
  funcionando sin cambios. En caso de necesitar coinstalación con
  `sale_layout_category_hide_detail`, fusionar manualmente su `t-if` en nuestro
  span o ajustar el xpath de aquel.

---

## Estructura de archivos

```
klo_invoice_report_price_unit_untaxed/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_move_line.py          # Campo computado price_unit_untaxed
├── report/
│   └── account_report_templates.xml  # Herencia de account.report_invoice_document
└── static/
    └── description/
        ├── icon.png
        └── Technical_context.md
```

---

## Instalación / Actualización

Instalación (primera vez):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -i klo_invoice_report_price_unit_untaxed \
    --stop-after-init
```

Actualización (tarea de desarrollo habitual):

```bash
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d <nombre_base_datos> \
    -u klo_invoice_report_price_unit_untaxed \
    --stop-after-init
```

> La base de datos activa se define en `db_name` de `config/odoo.conf`; no
> hardcodear el nombre de la base de datos.

---

## Posibles adaptaciones futuras

- Variantes de informe que heredan `account.report_invoice_document` (p. ej. módulos
  OCA de facturae, plantillas de cliente) quedan cubiertas automáticamente salvo que
  reemplacen a su vez el mismo span de `td_price_unit` (verificar colisión de xpaths,
  ver "Conflicto conocido" en "Vistas modificadas").
- Si se quisiera mostrar además el precio unitario **con descuento** aplicado (sin
  impuestos), extender el compute con `(1 - line.discount / 100.0) * price_unit_untaxed`
  o añadir un campo `price_unit_untaxed_discounted` siguiendo el patrón del portal
  de ventas del módulo de referencia.
- Notas de crédito y abonos usan el mismo template, por lo que ya quedan cubiertos
  sin cambios adicionales.
- Replicar el patrón en otros documentos (albaranes, compras) si el cliente lo
  pidiera, creando un módulo por documento con esta misma estructura.

---

## Datos de configuración

Ninguno. El módulo no carga datos iniciales, secuencias, grupos ni parámetros, y no
incluye datos demo (convención KLO).

---

## Comportamiento esperado

| Situación | Resultado en columna "Unit Price" |
|-----------|-----------------------------------|
| Impuesto configurado como **precio incluido** | Se extrae el precio base sin IVA (`compute_all → total_excluded`) |
| Impuesto configurado como **precio excluido** | El precio ya es sin IVA; `total_excluded` coincide con `price_unit` |
| Línea sin impuestos | Se muestra directamente `price_unit` |
| Línea de sección / nota / `cogs` / término de pago | El informe core no renderiza la celda; el campo vale `0.0` sin pasar por `compute_all` |
| Factura en divisa extranjera (multi-moneda) | El cálculo usa `line.currency_id`; el render con `t-field` muestra los decimales de `min_display_digits='Product Price'`, sin símbolo de moneda (el formato no depende de la divisa) |
| Portal de facturas (`/my/invoices/<id>`, vista previa HTML) | Mismo comportamiento: reutiliza `account.report_invoice_document` |

---

## Notas para IA / desarrollador

- **Campo clave:** `account.move.line.price_unit_untaxed` — Float no almacenado, se
  calcula al vuelo en el render del informe.
- **Template clave:** `account.report_invoice_document` — QWeb del PDF de factura;
  también usado como HTML en el portal de facturas del cliente.
- **Método clave:** `_compute_price_unit_untaxed` en `account.move.line` — envuelve
  `tax_ids.compute_all(...)` con `quantity=ESCALA` (10000.0) y toma
  `total_excluded / ESCALA`.
- **Consideraciones:**
  - `tax_ids` (Many2many), no `tax_id`: diferencia clave respecto a `sale.order.line`.
  - `partner_id` y `currency_id` existen en la propia línea; no bajar a `move_id`.
  - Licencia AGPL-3 según la convención vigente de AGENTS.md (el módulo de
    referencia de venta quedó igualmente unificado a AGPL-3 en 18.0.2.0.1).
  - Coexistencia con terceros: el reemplazo se limita al `<span>` de `td_price_unit`
    (ver "Conflicto conocido" en "Vistas modificadas"). Herencias dirigidas al
    `<td>` siguen funcionando; las dirigidas al span con `t-field='line.price_unit'`
    (p. ej. `sale_layout_category_hide_detail`) colisionan y exigen fusión manual.

---

## Historial de cambios

| Versión    | Fecha      | Descripción del cambio |
|------------|------------|------------------------|
| 18.0.1.0.0 | 2026-10-20 | Versión inicial y revisión de calidad: xpath limitado al `<span>` de `td_price_unit` (antes reemplazaba el `<td>` completo), terminología "sin impuestos" en el manifest, documentado conflicto con `sale_layout_category_hide_detail` |
| 18.0.2.0.0 | 2026-10-22 | Precisión y formato: `digits='Product Price'` → `min_display_digits='Product Price'`; el compute llama a `compute_all` con `quantity=ESCALA` (10000.0) y divide `total_excluded` entre `ESCALA` para anular el redondeo a céntimos; el span pasa de `t-out` + widget `monetary` a `t-field` (mismos decimales que el formulario vía `min_display_digits`, sin símbolo de moneda) |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**
Especialistas en personalización e implantación de Odoo ERP.
[www.klo.es](https://www.klo.es)
