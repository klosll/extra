# KLO — Open PDF Reports and PDF Attachments in Browser (prt_report_attachment_preview)

**Nombre técnico:** `prt_report_attachment_preview`  
**Versión:** 18.0.1.0.0  
**Autor original:** Ivan Sokolov, Cetmix  
**Adaptaciones KLO:** KLO Ingeniería Informática S.L.L.  
**Licencia:** LGPL-3  
**Categoría:** Productivity  
**Dependencias:** `web`  
**Ubicación:** `extra-addons/klo/extra/prt_report_attachment_preview`

---

## Descripción

Módulo que modifica el comportamiento por defecto de Odoo para la generación de informes PDF:
en lugar de descargar el fichero PDF al sistema local del usuario, lo **abre directamente en
una nueva pestaña del navegador** (vista previa en línea).

Incluye adaptaciones KLO para gestionar correctamente casos donde los `docids` de la URL
del reporte no corresponden al modelo del informe (p.ej. cuando el cliente JS pasa el ID
del picking activo a un reporte de `product.template`).

---

## Estructura del módulo

```
prt_report_attachment_preview/
├── __init__.py
├── __manifest__.py
├── LICENSE
├── pyproject.toml
├── README.rst
├── controllers/
│   ├── __init__.py
│   └── report.py                  ← Controlador HTTP principal (adaptado por KLO)
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   ├── banner.png
│   │   └── Tecnical_document.md   ← Este documento
│   └── src/
│       └── js/
│           ├── report.esm.js      ← Handler JS para ir.actions.report
│           └── tools.esm.js       ← Utilidades JS: construcción de URL, mensajes
├── tests/
│   ├── __init__.py
│   └── test_cx_report_controller.py
└── readme/
    ├── DESCRIPTION.md
    └── HISTORY.md
```

---

## Funcionamiento técnico

### Flujo de impresión PDF en Odoo estándar

1. El usuario pulsa "Imprimir" en un formulario/lista
2. El cliente JS recibe una acción `ir.actions.report` de tipo `qweb-pdf`
3. El módulo intercepta la acción antes del handler estándar de Odoo
4. Construye la URL del reporte incluyendo los `active_ids` del contexto
5. Abre la URL en una nueva pestaña del navegador en lugar de descargarla

### Interceptación JS (`report.esm.js`)

El módulo registra un handler en `registry.category("ir.actions.report handlers")` con
**sequence=10** (se ejecuta antes del handler estándar de Odoo):

```javascript
registry.category("ir.actions.report handlers").add(
    "open_report_handler",
    async function (action, options, env) {
        if (action.type === "ir.actions.report" && action.report_type === "qweb-pdf") {
            // Verifica estado de wkhtmltopdf
            // Abre PDF en nueva pestaña con browser.open(url, "_blank")
            return true;  // Consume la acción, no pasa al handler estándar
        }
        return false;  // Para otros tipos, deja pasar al siguiente handler
    },
    {sequence: 10}
);
```

### Construcción de URL (`tools.esm.js`)

La función `_getReportUrl` construye la URL del PDF:

```javascript
export const _getReportUrl = (action, type, env) => {
    const url = new URL(`/report/${type}/${action.report_name}`, baseUrl);

    // ⚠️ PUNTO CRÍTICO: añade active_ids como docids aunque no correspondan al modelo
    if (actionContext.active_ids) {
        url.pathname += `/${actionContext.active_ids.join(",")}`;
    }
    // ...
};
```

> **Nota KLO:** Esta lógica añade siempre los `active_ids` del contexto como `docids`
> en la URL, incluso cuando el reporte usa un modelo diferente al del registro activo
> (p.ej. picking ID → reporte de product.template). Esto genera el error `MissingError`
> que se resuelve en el controlador Python (ver sección Adaptaciones KLO).

### Controlador Python (`controllers/report.py`)

Clase `CxReportController` que hereda de `ReportController` (Odoo base) y sobrescribe
la ruta `/report/<converter>/<reportname>/<docids>`:

**Solo intercepta peticiones PDF** (`converter == "pdf"`). Para otros formatos delega
al controlador padre con `super()`.

#### Método `report_routes`

Gestiona el ciclo completo de generación del PDF:

1. Obtiene el objeto `ir.actions.report` por `reportname`
2. Procesa `options` y `context` de los parámetros GET
3. Gestiona `allowed_company_ids` desde el parámetro `cid`
4. **Verifica acceso** a los registros indicados en `docids` (con manejo de `MissingError`)
5. Compone el nombre del fichero PDF
6. Genera el PDF con `_render_qweb_pdf`
7. Devuelve el PDF con cabecera `Content-Disposition: inline` para vista en navegador

#### Método `_compose_report_file_name`

Compone el nombre del fichero PDF:
- **Sin docids:** usa el nombre del reporte
- **1 registro existente + `print_report_name`:** evalúa la expresión de nombre dinámica
- **Múltiples registros:** `"<nombre_reporte> x<cantidad>"`
- **0 registros existentes:** usa el nombre del reporte (caso registros no encontrados)

#### Método `_get_extra_context_for_single_record`

Utilidad que extrae variables de la expresión `print_report_name` para rellenar las no
reconocidas con el string `"report"` y evitar errores de evaluación.

---

## Adaptaciones KLO

### Problema resuelto

**Error original:**
```
odoo.exceptions.MissingError: El registro no existe o ha sido eliminado.
(Registro: product.template(400,), Usuario: 2)
```

**Causa:** Al imprimir etiquetas desde `stock.picking` (WH/IN/00031, ID=400), el wizard
`product.label.layout` devuelve una acción con `docids=None`. El cliente JS
(`tools.esm.js`) añade automáticamente `active_ids=[400]` (el ID del picking) como
`docids` en la URL. El controlador intenta verificar acceso en `product.template(400)`,
que no existe porque el modelo del reporte es `product.template` pero el ID `400`
pertenece a `stock.picking`.

**Flujo del error:**
```
Usuario → "Acción → Imprimir → Etiquetas" (picking ID=400)
  → picking.label.type wizard → product.label.layout wizard
  → report_action(None, data={...})        # docids=None
  → JS: active_ids=[400] → URL: /report/pdf/product.report_.../400
  → CxReportController.report_routes()
  → product.template.browse([400]).check_access_rule("read")
  → MissingError ❌
```

### Cambios aplicados en `controllers/report.py`

#### 1. Import de `MissingError`

```python
from odoo.exceptions import MissingError
```

#### 2. Manejo de `MissingError` en `report_routes` (líneas ~165-182)

```python
# Handle document IDs
doc_ids: list[int] = []
if docids:
    try:
        doc_ids = [int(i) for i in docids.split(",")]
        records = request.env[report.model].browse(doc_ids)
        try:
            records.check_access_rule("read")
        except MissingError:
            # Algunos registros no existen (p.ej. picking ID pasado a un reporte
            # de product.template). Se filtran los existentes; el reporte usará
            # el data dict con los IDs correctos de producto.
            existing = records.exists()
            if existing:
                existing.check_access_rule("read")
            doc_ids = existing.ids
    except (ValueError, AttributeError):
        return request.not_found()
```

**Efecto:** Cuando los `docids` de la URL no corresponden al modelo del reporte,
se filtran con `.exists()`. Si ninguno existe, `doc_ids` queda vacío y el reporte
se renderiza únicamente con el `data` dict (que contiene `quantity_by_product` con
los IDs de producto correctos preparados por el wizard).

#### 3. Protección en `_compose_report_file_name` (líneas ~79-106)

```python
if docids:
    try:
        records = request.env[report.model].browse(docids)
        records = records.exists()   # Filtra a existentes
    except Exception:
        records = request.env[report.model]  # Vacío en caso de error
    record_count = len(records)      # Usa len(records), no len(docids)
    if record_count == 0:
        report_name = report.name    # Fallback si todos eran huérfanos
    elif record_count == 1 and report.sudo().print_report_name:
        # ... nombre dinámico para registro único
```

---

## Casos de uso afectados

| Caso | Antes de la adaptación | Después |
|------|------------------------|---------|
| Imprimir etiquetas desde `stock.picking` | `MissingError` si el picking ID no existe como `product.template` | ✅ Se filtran IDs inexistentes, el wizard genera las etiquetas correctamente |
| Imprimir cualquier reporte PDF normal | ✅ Funcionaba | ✅ Sigue funcionando |
| Reporte con `docids` correctos | ✅ Funcionaba | ✅ Sigue funcionando |
| Nombre de fichero PDF con registros huérfanos | Posible error | ✅ Usa nombre del reporte como fallback |

---

## Verificación de la base de datos

Antes de aplicar la adaptación se verificó que **no existen registros huérfanos** en
las bases de datos del proyecto que pudieran causar el error por datos corruptos:

```sql
-- Resultado en todas las BDs (ryp_dev, victorperez_dev, klo_dev, etc.): 0 huérfanos
SELECT COUNT(*) FROM product_product pp
WHERE NOT EXISTS (SELECT 1 FROM product_template pt WHERE pt.id = pp.product_tmpl_id);
```

La causa real del error es la **coincidencia de IDs** entre `stock.picking` (ID=400)
y el modelo `product.template` del reporte de etiquetas, no registros eliminados.

---

## Endpoints HTTP

| Ruta | Tipo | Auth | Descripción |
|------|------|------|-------------|
| `/report/pdf/<reportname>` | HTTP GET | user | Genera y muestra PDF sin docids |
| `/report/pdf/<reportname>/<docids>` | HTTP GET | user | Genera y muestra PDF para los docids |
| `/report/check_wkhtmltopdf` | JSON RPC | user | Verifica el estado de wkhtmltopdf |

---

## Dependencias técnicas

| Componente | Tipo | Descripción |
|------------|------|-------------|
| `odoo.addons.web.controllers.report.ReportController` | Python class | Clase base que se hereda y extiende |
| `odoo.exceptions.MissingError` | Python exception | Capturada para manejar IDs inexistentes |
| `ir.actions.report` | Odoo model | Usado para obtener info del reporte por nombre |
| `registry("ir.actions.report handlers")` | JS registry | Punto de registro del handler JS (sequence=10) |
| `wkhtmltopdf` | Sistema | Requerido para generación de PDF |

---

## Notas para futuras adaptaciones

1. **Si se quiere cambiar el comportamiento de apertura** (p.ej. descargar en lugar de
   abrir en pestaña), modificar `report.esm.js`: cambiar `browser.open(url, "_blank")`
   por el mecanismo de descarga de Odoo (`download` service).

2. **Si el error `MissingError` aparece en otros modelos**, la lógica de `report_routes`
   ya lo maneja genéricamente para cualquier combinación modelo/docids.

3. **La función `_getReportUrl` en `tools.esm.js`** es la que añade `active_ids` como
   docids. Si en el futuro se quiere evitar esto para modelos específicos, habría que
   añadir lógica condicional en esa función comparando `action.res_model` con el modelo
   esperado por el reporte.

4. **El handler JS tiene `sequence: 10`**, lo que significa que se ejecuta antes que el
   handler estándar de Odoo. Si otros módulos registran handlers con sequence < 10,
   podrían interferir.

5. **Compatible con los módulos OCA** `report_xml`, `report_xlsx_helper` y `report_xlsx`
   (visibles en el traceback del error): todos ellos delegan a `super()` para PDF, por
   lo que el controlador KLO los recibe correctamente.

---

## Historial de cambios KLO

| Fecha | Versión | Descripción |
|-------|---------|-------------|
| 2026-04-16 | 18.0.1.0.0+klo1 | Adaptación para manejar `MissingError` cuando `docids` no corresponden al modelo del reporte (fix impresión de etiquetas desde `stock.picking`) |

