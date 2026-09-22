# Technical Context — `klo_web_enter_as_tab`

## Módulo
| Campo | Valor |
|---|---|
| **Nombre técnico** | `klo_web_enter_as_tab` |
| **Nombre legible** | KLO - Enter como Tab en listas editables |
| **Versión** | 18.0.1.0.2 |
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

## Vistas / Templates QWeb modificados

### 1) `web.ListRenderer.RecordRow` — habilita navegación en columnas `widget`

**Archivo:** `static/src/xml/list_renderer_patch.xml`  
**Template heredado:** `web.ListRenderer.RecordRow` (`addons/web/static/src/views/list/list_renderer.xml` :279)  
**Motivo:** El `<td>` de tipo `widget` **no tenía** `t-on-keydown` en el core. Sin él Enter remapeado no llegaba a `onCellKeydown`.

```xml
<t t-inherit="web.ListRenderer.RecordRow" t-inherit-mode="extension">
    <xpath expr="//t[@t-if=&quot;column.type === 'widget'&quot;]/td" position="attributes">
        <attribute name="t-on-keydown">(ev) =&gt; this.onCellKeydown(ev, group, record)</attribute>
        <attribute name="tabindex">-1</attribute>
    </xpath>
</t>
```

### 2) `sale_order_line_price_history.price_history_widget` — salto del icono Historial

**Archivo:** mismo `list_renderer_patch.xml` (segundo `t-inherit`)  
**Template heredado:** `sale_order_line_price_history.price_history_widget` (`extra-addons/oca/sale-workflow/.../sale_line_price_history_widget.xml`)  
**Motivo / Requisito cliente:** Que **Tab/Enter no se detenga en el icono** `fa-history` (reloj con flecha), sino que salte directo a la siguiente columna editable. El widget original trae `tabindex="0"` (focalizable); se pasa a `-1` para que `getTabableElements()` (`core/utils/ui.js:121 TABABLE_SELECTOR :not([tabindex="-1"])`) y el Tab nativo lo ignoren. Sigue siendo clicable con ratón. `findNextFocusableOnRow`/`findPreviousFocusableOnRow` ya descartan celdas sin elemento tabbeable (`getElementToFocus(c) === c`), por lo que el salto es automático en ambas direcciones.

```xml
<t t-inherit="sale_order_line_price_history.price_history_widget" t-inherit-mode="extension">
    <xpath expr="//a[contains(@class,'fa-history')]" position="attributes">
        <attribute name="tabindex">-1</attribute>
    </xpath>
</t>
```

Afecta a `sale.order` → `order_line` y a cualquier widget futuro que se quiera hacer “skippeable”. No hay `column_invisible` ni `attrs` involucrados.

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
│       ├── js/
│       │   └── list_enter_as_tab.js  ← Patch ListRenderer.onCellKeydown (Enter→Tab)
│       └── xml/
│           └── list_renderer_patch.xml ← Herencia QWeb para td widget (history icon)
```

Manifest `assets`:
```python
"assets": {
    "web.assets_backend": [
        "klo_web_enter_as_tab/static/src/js/list_enter_as_tab.js",
        "klo_web_enter_as_tab/static/src/xml/list_renderer_patch.xml",
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
| Historial precios (`fa-history`) al tabular con **Tab/Enter** | Se detenía en el icono y requería otro Tab; Enter abría wizard | **Se salta** — Tab/Enter van directo a siguiente columna editable. Historial solo por click. |
| Última columna editable, pulsa **Enter** (fila intermedia) | Salta a primera columna de siguiente línea | Igual que Tab: salta a siguiente línea (comportamiento Tab nativo) |
| Última columna de última fila, pulsa **Enter** con línea sucia | Crea nueva línea | Crea nueva línea (Tab también lo hace vía `applyCellKeydownEditModeGroup`) |
| **Shift+Enter** / **Shift+Tab** en edición | Valida/salta atrás | **Retrocede saltando el historial** igual que Shift+Tab |
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

* **Fichero clave JS:** `static/src/js/list_enter_as_tab.js` — patch `onCellKeydown`. **Fichero clave XML:** `static/src/xml/list_renderer_patch.xml` — 2 inherits: habilita `t-on-keydown` en `td widget` y pone `tabindex="-1"` al `fa-history`.
* **Skip historial:** `sale_order_line_price_history/static/src/xml/sale_line_price_history_widget.xml` traía `tabindex="0"`; se parchea a `-1` para que `getTabableElements` (`TABABLE_SELECTOR :not([tabindex="-1"])`) y `findNextFocusableOnRow` lo salten. Antes de 18.0.1.0.1 sí se detenía; desde 18.0.1.0.2 se salta.
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
| 18.0.1.0.1 | 2026-09-22 | Fix widget Historial (`fa-history`): añade `t-on-keydown` a `td` tipo widget para que Enter→Tab avance igual que Tab |
| 18.0.1.0.2 | 2026-09-22 | Historial no focalizable: `tabindex="-1"` al `fa-history` para que Tab/Enter lo salten y vayan directo a siguiente columna |

---

## Sobre KLO

**KLO Ingeniería Informática S.L.L.**  
Especialistas en personalización e implantación de Odoo ERP.  
[www.klo.es](https://www.klo.es)
