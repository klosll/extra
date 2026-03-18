/** @odoo-module **/

/**
 * Parche del ListController para account.move:
 *
 *  - openRecord : al EDITAR una factura existente, si su diario tiene
 *                 es_para_uva = True se abre view_move_form_uva.
 *
 *  - createRecord: al crear UNA NUEVA factura, se consulta al servidor si el
 *                  diario predeterminado del contexto actual tiene es_para_uva.
 *                  Si es así, se abre view_move_form_uva en lugar del formulario
 *                  estándar.
 *
 * NOTA sobre this._super en métodos async:
 *   El mecanismo de patch de Odoo 16 configura this._super de forma síncrona
 *   y lo restaura inmediatamente tras el retorno de la función parcheada.
 *   En funciones async, el retorno es una Promise, por lo que _super se
 *   restaura ANTES de que el código async termine. La solución es guardar
 *   this._super en una variable local ANTES del primer await.
 */

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, "klo_account_invoice_uva.list_controller_open_record", {

    /**
     * Intercepta la apertura de un registro existente.
     * El campo es_para_uva se carga en la lista como columna invisible,
     * por lo que está disponible en record.data sin llamada extra al servidor.
     */
    async openRecord(record) {
        // Guardar _super ANTES del primer await (ver nota sobre async en cabecera)
        const superFn = this._super.bind(this);

        if (this.props.resModel === "account.move" && record.data.es_para_uva) {
            // get_formview_action → get_formview_id → view_move_form_uva
            const action = await this.orm.call(
                "account.move",
                "get_formview_action",
                [[record.resId]],
            );
            // Propagar los resIds activos para la navegación entre registros
            const activeIds = this.model.root.records.map((dp) => dp.resId);
            action.context = {
                ...action.context,
                active_id: record.resId,
                active_ids: activeIds,
                active_model: "account.move",
            };
            return this.actionService.doAction(action);
        }
        // Comportamiento estándar para facturas normales y otros modelos
        return superFn(record);
    },

    /**
     * Intercepta la creación de un nuevo registro.
     * Consulta al servidor si el diario predeterminado del contexto actual tiene
     * es_para_uva = True. Si es así, abre view_move_form_uva para el nuevo
     * registro en lugar del formulario estándar.
     */
    async createRecord() {
        // Guardar _super ANTES del primer await (ver nota sobre async en cabecera)
        const superFn = this._super.bind(this);

        if (this.props.resModel === "account.move") {
            const viewId = await this.orm.call(
                "account.move",
                "get_uva_formview_id_for_new",
                [],
                { context: this.props.context },
            );
            if (viewId) {
                // Abrir el formulario de uva para un nuevo registro (sin resId)
                return this.actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "account.move",
                    view_mode: "form",
                    views: [[viewId, "form"]],
                    target: "current",
                    context: this.props.context,
                });
            }
        }
        // Comportamiento estándar para facturas normales y otros modelos
        return superFn();
    },
});
