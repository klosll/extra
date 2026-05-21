/** @odoo-module **/

/**
 * KLO - Corrección del bug de zona horaria en el módulo OCA date_range
 *
 * PROBLEMA (date_range.esm.js del módulo OCA):
 * El método _setDefaultValue usaba moment() (hora local del navegador/servidor)
 * en lugar de moment.utc() para construir los objetos Moment de inicio y fin del rango.
 *
 * En España (UTC+1 en invierno / CET), esto provoca que:
 *   moment('2026-01-01 00:00:00')  →  2025-12-31T23:00:00Z  →  parseDate → '2025-12-31'
 *
 * Resultado: el dominio generado era date >= '2025-12-31', incluyendo datos del año anterior.
 *
 * ESCENARIO QUE ACTIVA EL BUG:
 * 1. Los rangos de años anteriores están archivados (active=False)
 * 2. El primer rango activo visible (p.ej. M01-26) pasa a ser el valor por defecto
 * 3. El usuario no necesita cambiar el dropdown (ya muestra M01-26)
 * 4. onValueChange (que sí usa moment.utc) nunca se llama
 * 5. onApply usa las fechas incorrectas de _setDefaultValue
 *
 * SOLUCIÓN: sobreescribir _setDefaultValue para usar moment.utc() consistentemente
 * con onValueChange (que ya lo hacía correctamente).
 */

import { patch } from "@web/core/utils/patch";
import { FIELD_TYPES } from "web.searchUtils";
import CustomFilterItem from "web.CustomFilterItem";

// KLO. Parche corrector aplicado SOBRE el parche del módulo OCA date_range
patch(CustomFilterItem.prototype, "klo_date_range_error_fix.CustomFilterItem", {
    /**
     * Sobreescribe _setDefaultValue del parche de date_range para corregir
     * el uso de moment() (hora local) por moment.utc() en rangos de tipo date_range.
     *
     * @override (sobreescribe el parche de date_range, que sobreescribe el original)
     */
    _setDefaultValue(condition) {
        // KLO. Verificar que this.OPERATORS y this.date_ranges estén disponibles
        // (pueden no estar si _computeDateRangeOperators aún no ha terminado su RPC)
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
                const default_range = this.date_ranges[operator.date_range_type] &&
                                      this.date_ranges[operator.date_range_type][0];
                if (default_range) {
                    // KLO. CORRECCIÓN: usar moment.utc() en lugar de moment() para evitar
                    // el desfase de zona horaria (UTC+1 en España en invierno hace que
                    // '2026-01-01 00:00:00 CET' sea '2025-12-31T23:00:00Z' en UTC,
                    // lo que parseDate convierte a '2025-12-31' → datos del año anterior
                    // aparecen en el filtro).
                    const d_start = moment.utc(`${default_range.date_start} 00:00:00`);
                    const d_end = moment.utc(`${default_range.date_end} 23:59:59`);
                    condition.value = [d_start, d_end];
                    return;
                }
            }
        }
        // Delegar al parche anterior (date_range) que a su vez llama al original
        this._super(...arguments);
    },
});

