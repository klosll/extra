/** @odoo-module **/

/**
 * KLO - Corrección del bug de zona horaria en el módulo OCA date_range
 *
 * ═══════════════════════════════════════════════════════════════════════════
 * DIAGNÓSTICO TÉCNICO COMPLETO
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * FLUJO DE DATOS (date_range → dominio Odoo):
 *   1. _computeDateRangeOperators: RPC trae rangos desde BD → guardados en this.date_ranges
 *   2. _setDefaultValue: establece condition.value = [d_start, d_end] al ABRIR el filtro
 *   3. onValueChange: actualiza condition.value cuando el USUARIO cambia el dropdown
 *   4. _getPreFilters → field_utils.parse[type](val, {type}, {timezone:true}) convierte
 *      los Moment objects a strings de dominio ('YYYY-MM-DD' para date)
 *
 * BUG EN OCA date_range.esm.js (_setDefaultValue, líneas 55-56):
 *   moment('2026-01-01 00:00:00')  ← hora LOCAL del navegador
 *
 *   En España (CET=UTC+1 invierno, CEST=UTC+2 verano):
 *     - Enero (UTC+1):  local 2026-01-01 00:00 → UTC 2025-12-31T23:00:00Z
 *     - Junio (UTC+2):  local 2026-06-01 00:00 → UTC 2026-05-31T22:00:00Z
 *
 *   parseDate convierte via moment.utc(localMoment) → representación UTC
 *   → .format('YYYY-MM-DD') → '2025-12-31' ← AÑO ANTERIOR ❌
 *
 * CORRECCIÓN: moment.utc('YYYY-MM-DD HH:mm:ss') crea Moment directamente en UTC:
 *   moment.utc('2026-01-01 00:00:00') → 2026-01-01T00:00:00Z
 *   parseDate → '2026-01-01' ✓
 *
 * ESCENARIO QUE ACTIVA EL BUG (VPS Alemania, verano CEST/UTC+2):
 *   1. Rangos de años anteriores archivados (active=False)
 *   2. Primer rango activo (M01-26) aparece como valor por defecto en el dropdown
 *   3. Usuario no cambia el dropdown → onValueChange (que usa moment.utc ✓) NUNCA se llama
 *   4. _setDefaultValue (que usa moment() ❌) establece valores erróneos
 *   5. onApply genera dominio: date >= '2025-12-31' → incluye datos del 31/12/2025
 *
 * BUG HISTÓRICO EN ESTE MÓDULO (corregido 2026-06-15 v15.0.1.0.1):
 *   El manifest referenciaba 'klo_date_range_error_correction/...' (nombre antiguo del
 *   módulo antes de renombrarlo a klo_date_range_error_fix), por lo que el asset JS
 *   nunca se cargaba y la corrección no tenía efecto en ningún entorno.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { patch } from "@web/core/utils/patch";
import { FIELD_TYPES } from "web.searchUtils";
import CustomFilterItem from "web.CustomFilterItem";

// KLO. Parche corrector cargado DESPUÉS del parche OCA date_range (garantizado por
// la dependencia de módulo), sobreescribiendo los métodos con la versión UTC correcta.
patch(CustomFilterItem.prototype, "klo_date_range_error_fix.CustomFilterItem", {

    /**
     * Sobreescribe _setDefaultValue del parche OCA date_range para corregir
     * el uso de moment() [hora local] por moment.utc() [UTC explícito].
     *
     * field_utils.parse.date() hace internamente moment.utc(momentObject):
     * si el Moment es local (UTC+2), '2026-01-01 00:00 local' → '2025-12-31T22:00Z'
     * → .format('YYYY-MM-DD') → '2025-12-31' (datos del año anterior en el dominio).
     *
     * @override
     */
    _setDefaultValue(condition) {
        // KLO. Verificar disponibilidad de datos del RPC asíncrono
        if (
            this.OPERATORS &&
            this.date_ranges &&
            this.fields[condition.field]
        ) {
            const type = this.fields[condition.field].type;
            const fieldTypeKey = FIELD_TYPES[type];
            const operators = this.OPERATORS[fieldTypeKey];
            const operator = operators && operators[condition.operator];

            if (operator && operator.date_range) {
                const rangesForType = this.date_ranges[operator.date_range_type];
                const default_range = rangesForType && rangesForType[0];
                if (default_range) {
                    // KLO. CORRECCIÓN ZONA HORARIA: moment.utc() → 2026-01-01T00:00:00Z
                    // moment() sin utc con UTC+2 → 2025-12-31T22:00:00Z → '2025-12-31' ❌
                    const d_start = moment.utc(`${default_range.date_start} 00:00:00`);
                    const d_end = moment.utc(`${default_range.date_end} 23:59:59`);
                    condition.value = [d_start, d_end];
                    return; // KLO. No llamar al _super() buggy de OCA
                }
            }
        }
        // KLO. Sin operador date_range → delegar al parche OCA → original Odoo
        this._super(...arguments);
    },

    /**
     * Sobreescribe onValueChange para que este parche sea autosuficiente.
     * OCA ya usa moment.utc() aquí correctamente, pero lo duplicamos para
     * protegernos ante futuras actualizaciones del módulo OCA.
     *
     * @override
     */
    onValueChange(condition, ev) {
        if (
            this.OPERATORS &&
            this.date_ranges &&
            this.fields[condition.field]
        ) {
            const type = this.fields[condition.field].type;
            const fieldTypeKey = FIELD_TYPES[type];
            const operators = this.OPERATORS[fieldTypeKey];
            const operator = operators && operators[condition.operator];

            if (operator && operator.date_range) {
                const eid = parseInt(ev.target.value);
                const ranges = this.date_ranges[operator.date_range_type];
                const range = ranges && ranges.find((x) => x.id === eid);
                if (range) {
                    // KLO. CORRECCIÓN ZONA HORARIA: moment.utc() explícito
                    const d_start = moment.utc(`${range.date_start} 00:00:00`);
                    const d_end = moment.utc(`${range.date_end} 23:59:59`);
                    condition.value = [d_start, d_end];
                    return;
                }
            }
        }
        // KLO. Sin operador date_range → delegar al parche OCA → original Odoo
        this._super(...arguments);
    },
});
