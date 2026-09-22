/** @odoo-module **/

import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
    /**
     * Hace que Enter se comporte como Tab en las listas editables x2many.
     * Se re-mapea la tecla del evento a "Tab" antes de delegar en la
     * implementación original, de modo que toda la lógica interna (navegación
     * entre celdas, creación de líneas, grupos, multi-edición) se comporta
     * exactamente igual que con Tab. Shift+Enter equivale a Shift+Tab.
     * Excepción: dentro de un TEXTAREA se mantiene el Enter nativo.
     */
    onCellKeydown(ev, group = null, record = null) {
        const hotkey = getActiveHotkey(ev);
        const isEnterHotkey = hotkey === "enter" || hotkey === "shift+enter";
        // Solo en modo edición (líneas x2many editables) y nunca dentro de TEXTAREA
        // En modo solo-lectura se preserva el comportamiento nativo de Enter
        // (abrir registro / entrar en edición) para no romper la navegación estándar.
        if (isEnterHotkey && this.editedRecord && ev.target.tagName !== "TEXTAREA") {
            Object.defineProperty(ev, "key", {
                value: "Tab",
                configurable: true,
            });
            const result = super.onCellKeydown(ev, group, record);
            Object.defineProperty(ev, "key", {
                value: "Enter",
                configurable: true,
            });
            return result;
        }
        return super.onCellKeydown(ev, group, record);
    },
});