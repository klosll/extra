# Technical Context — `klo_web_enter_as_tab`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_web_enter_as_tab` |
| **Nombre legible** | KLO - Enter como Tab en listas editables |
| **Versión** | 18.0.1.0.0 |
| **Autor** | KLO Ingeniería Informática S.L.L. |
| **Licencia** | AGPL-3 |
| **Website** | https://www.klo.es |
| **Categoría** | Technical |
| **Ubicación** | `/opt/odoo18_desarrollo/extra-addons/klo/extra/klo_web_enter_as_tab/` |
| **Fecha creación** | 2026-09-22 |
| **Odoo versión** | 18.0 Community |

---

## Descripción

En Odoo 18 Community, las **listas editables x2many** (ej. líneas de pedido `sale.order.line`, `purchase.order.line`, líneas de factura, albarán, etc.) tienen un comportamiento de teclado distinto según la tecla:

* **Tab** → avanza a la siguiente celda editable de la misma fila (siguiente columna). Solo al llegar a la última columna crea/salta a la siguiente línea.
* **Enter** → valida la línea y salta a la línea siguiente o crea una nueva línea (`editable="bottom"`).

Para usuarios que introducen datos en ráfaga, **Enter resulta disruptivo**: crea líneas vacías involuntarias. Este módulo hace que **Enter se comporte exactamente como Tab** (y **Shift+Enter como Shift+Tab**) **solo en modo edición**, manteniendo Enter nativo en `TEXTAREA` (notas, descripciones largas) y en modo solo-lectura (donde Enter abre el registro).

Resultado: el usuario puede tabular con Intro sin cambiar su flujo de trabajo.

---

## Problema que resuelve / compatibilidad entre versiones

| Versión Odoo | Tecnología | Fichero clave |
|---|---|---|
| ≤16 | Legacy JS `web.ListRenderer` (`require`) | `web/static/src/js/views/list/list_renderer.js` |
| 17+ / 18.0 | OWL 2 `ListRenderer` (`@web/views/list/list_renderer`) | `addons/web/static/src/views/list/list_renderer.js` |

Odoo 17+ migró a OWL y al sistema `patch()` (`@web/core/utils/patch`). El manejo de teclado ahora está centralizado en `ListRenderer.onCellKeydown()` que delega en `getActiveHotkey()` (`@web/core/hotkeys/hotkey_service`). Este módulo está escrito **solo para Odoo 18 OWL** y no es retrocompatible con la API antigua sin adaptación.

**Puntos de incompatibilidad detectados:**
* `getActiveHotkey(ev)` normaliza `ev.key.toLowerCase()` + modificadores (`shift`, `control`, `alt`). Por eso `Enter` → `"enter"` y `Shift+Enter` → `"shift+enter"`.
* `ListRenderer.editedRecord` indica si la lista está en modo edición. Se usa para limitar el parcheo solo a edición y no romper el modo lectura.
* Excepción existente en core para `TEXTAREA` (líneas 1157-1159 de `list_renderer.js`): `if (ev.target.tagName === "TEXTAREA" && hotkey === "enter") return;`. El módulo respeta esa excepción.

---

## Dependencias

| Módulo | Propósito |
|---|---|
| `web` | Provee `ListRenderer` y `getActiveHotkey`; base de todas las vistas lista. |

Ubicación del fichero parcheado:
`/opt/odoo18_desarrollo/odoo/addons/web/static/src/views/list/list_renderer.js`

No depende de ningún módulo OCA ni de `sale`/`purchase` concreto: es **genérico** para cualquier vista lista editable (`editable="bottom"` o `editable="top"`).

---

## Lógica

### Método clave parcheado

**`ListRenderer.onCellKeydown(ev, group, record)`** — línea 1150 de `list_renderer.js`

Flujo original:
1. `const hotkey = getActiveHotkey(ev)` → `"enter"` / `"tab"` / `"shift+tab"` etc.
2. Si `ev.target.tagName === "TEXTAREA" && hotkey === "enter"` → `return` (permite salto de línea nativo).
3. Delega en `onCellKeydownEditMode` si `this.editedRecord`, si no en `onCellKeydownReadOnlyMode`.
4. Dentro de `onCellKeydownEditMode`:
   * `applyCellKeydownEditModeStayOnRow` gestiona `tab`/`shift+tab` → `findNextFocusableOnRow` / `findPreviousFocusableOnRow`
   * `applyCellKeydownEditModeGroup` gestiona `enter`/`tab` al final de grupo → `this.add({group})`
   * `switch (hotkey)` con `case "tab"` y `case "enter"` con lógicas distintas (tab navega celdas, enter salta de registro o crea línea).

### Implementación del módulo

Fichero: `static/src/js/list_enter_as_tab.js`

```javascript
/** @odoo-module **/
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
    onCellKeydown(ev, group = null, record = null) {
        const hotkey = getActiveHotkey(ev);
        const isEnterHotkey = hotkey === "enter" || hotkey === "shift+enter";
        if (isEnterHotkey && this.editedRecord && ev.target.tagName !== "TEXTAREA") {
            Object.defineProperty(ev, "key", { value: "Tab", configurable: true });
            const result = super.onCellKeydown(ev, group, record);
            Object.defineProperty(ev, "key", { value: "Enter", configurable: true });
            return result;
        }
        return super.onCellKeydown(ev, group, record);
    },
});
```

**Por qué re-mapear `ev.key` en lugar de duplicar lógica:**
* `getActiveHotkey` se llama de nuevo dentro de `super.onCellKeydown`, por lo que al cambiar `ev.key` a `"Tab"` (preservando `ev.shiftKey`) el hotkey resultante pasa automáticamente de `"enter"`→`"tab"` y `"shift+enter"`→`"shift+tab"` sin tocar nada más.
* Se reutiliza **toda** la lógica existente de navegación, creación de líneas, grupos y multi-edición. Cero duplicación, cero divergencia futura.
* Se restaura `ev.key` a `"Enter"` tras la llamada para no contaminar otros listeners.

### Condiciones / triggers

| Condición | Comportamiento |
|---|---|
| `hotkey` es `enter` o `shift+enter` **y** `this.editedRecord` existe **y** target no es `TEXTAREA` | Re-mapea a `tab` / `shift+tab` y delega al super |
| `TEXTAREA` con Enter | No interviene → salto de línea nativo |
| Modo solo-lectura (`!this.editedRecord`) | No interviene → Enter abre registro / entra en edición (comportamiento estándar) |
| Otras teclas (`tab`, flechas, etc.) | No interviene → comportamiento estándar |

---

## Vistas modificadas

Ninguna vista XML/QWeb se hereda. El cambio es 100% JS (assets). Afecta visualmente a **todas** las vistas lista donde `ListRenderer` esté en modo editable:

* Pedidos de venta: `sale.order` → `order_line` (`editable="bottom"`)
* Pedidos de compra: `purchase.order` → `order_line`
* Facturas: `account.move` → `invoice_line_ids`
* Albaranes, presupuestos, partes, y cualquier `One2many` con `editable` en su definición de vista.

No hay `column_invisible` ni `attrs` involucrados (Odoo 18 ya usa atributos individuales `invisible`, `readonly`, etc.).

---

## Estructura de archivos

```
klo_web_enter_as_tab/
├── __init__.py
├── __manifest__.py
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── Technical_context.md   ← Este fichero
│   └── src/
│       └── js/
│           └── list_enter_as_tab.js  ← Patch ListRenderer.onCellKeydown
```

Manifest `assets`:
```python
"assets": {
    "web.assets_backend": [
        "klo_web_enter_as_tab/static/src/js/list_enter_as_tab.js",
    ],
},
```

---

## Instalación / Actualización

La base de datos activa se lee siempre de `config/odoo.conf` (`db_name = laibanesa_dev` actualmente). **No hardcodear**.

```bash
# Instalar (primera vez)
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d laibanesa_dev -i klo_web_enter_as_tab --stop-after-init

# Actualizar (tras cambios en JS/manifest)
python odoo-bin -c /opt/odoo18_desarrollo/config/odoo.conf -d laibanesa_dev -u klo_web_enter_as_tab --stop-after-init

# Vía uv (equivalente, usado en _templates)
 /home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d laibanesa_dev -u klo_web_enter_as_tab --stop-after-init
```

Tras instalar/actualizar, **recargar el navegador con Ctrl+Shift+R** (limpiar caché de assets) para que `web.assets_backend` recargue el JS parcheado.

Logs: `tail -f /opt/odoo18_desarrollo/log/odoo.log`

---

## Comportamiento esperado

| Situación | Antes del módulo | Después del módulo |
|---|---|---|
| Edición x2many, foco en columna intermedia, pulsa **Enter** | Valida línea y crea/salta a siguiente línea | **Avanza a siguiente columna editable** (como Tab) |
| Última columna editable, pulsa **Enter** (fila intermedia) | Salta a primera columna de siguiente línea | Igual que Tab: salta a siguiente línea (comportamiento Tab nativo) |
| Última columna de última fila, pulsa **Enter** con línea sucia | Crea nueva línea | Crea nueva línea (Tab también lo hace vía `applyCellKeydownEditModeGroup`) |
| **Shift+Enter** en edición | Valida/salta atrás (o crea) | **Retrocede a columna anterior** (como Shift+Tab) |
| `TEXTAREA` con Enter | Salto de línea | **Salto de línea** (sin cambios) |
| Lista en solo-lectura, Enter sobre fila | Abre formulario del registro | **Abre formulario** (sin cambios) |

---

## Posibles adaptaciones futuras

* **Activación por modelo/vista:** Añadir un `registry` o `data-attribute` en la vista (`options="{'enter_as_tab': true}"`) para limitar el comportamiento solo a `sale.order`/`purchase.order` si se quiere granularidad. Actualmente es global a todas las listas editables.
* **Toggle por usuario:** Añadir un `res.config.settings` o preferencia de usuario (`ir.config_parameter` o campo en `res.users`) para activar/desactivar el comportamiento por usuario, útil si algunos usuarios prefieren el Enter clásico.
* **Soporte para Enter = Tab + Validación:** Si en el futuro se quiere que Enter además guarde parcialmente la línea antes de tabular, interceptar `list.leaveEditMode({validate:true})` antes del re-mapeo.
* **Migración a Odoo 19+:** Verificar si `ListRenderer` cambia a composición o si `getActiveHotkey` cambia su firma; el patch por `Object.defineProperty(ev, "key")` seguirá siendo válido mientras el hotkey se derive de `ev.key`.
* **Exclusión de campos específicos:** Si algún widget (ej. `many2many_tags`, `one2many` anidado) necesita Enter nativo, añadir condición `ev.target.closest(".o_field_many2many_tags")` para excluirlo.

---

## Notas para IA / desarrollador

* **Fichero clave:** `static/src/js/list_enter_as_tab.js` — único punto de lógica. No hay Python ni vistas.
* **Método clave:** `ListRenderer.onCellKeydown` en `/opt/odoo18_desarrollo/odoo/addons/web/static/src/views/list/list_renderer.js:1150`
* **Servicio hotkey:** `/opt/odoo18_desarrollo/odoo/addons/web/static/src/core/hotkeys/hotkey_service.js:58` — `getActiveHotkey(ev)` lowercased, por eso se compara con `"enter"`/`"shift+enter"`.
* **Asset bundle:** `web.assets_backend` — todo JS de backend se carga ahí; no usar `web.assets_frontend`.
* **Icono obligatorio:** `static/description/icon.png` copiado desde `extra-addons/klo/_templates/static/description/icon.png` (requisito AGENTS.md para todo `klo_*`).
* **Consideración de rendimiento:** Patch mínimo (una comparación + redefine property) sin listeners adicionales; impacto despreciable incluso en listas con cientos de filas.
* **Testing manual recomendado:** Abrir `Ventas > Pedidos > Crear`, añadir 2 líneas, tabular con Enter y Shift+Enter, probar TEXTAREA (nota interna), probar lista en solo-lectura (Enter debe abrir registro).

---

## Historial de cambios

| Versión | Fecha | Descripción del cambio |
|---|---|---|
| 18.0.1.0.0 | 2026-09-22 | Versión inicial: Enter como Tab en listas editables |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)
