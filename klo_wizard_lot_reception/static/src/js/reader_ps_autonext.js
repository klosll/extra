odoo.define('klo_wizard_lot_reception.reader_ps_autonext', function (require) {
"use strict";

var basicFields = require('web.basic_fields');
var fieldRegistry = require('web.field_registry');
var FormRenderer = require('web.FormRenderer');

// Enfoca el primer input reader_ps visible y hace scroll a su fila (la nueva
// línea, que con editable="bottom" queda al final). Reintenta para tolerar el
// retardo del onchange/re-render. Busca por data-field-name (que nuestro
// widget marca en el input) porque Odoo 14 no pone `name` en los inputs.
function focusReaderPs(attempts) {
    attempts = attempts || 40;
    var count = 0;
    var timer = setInterval(function () {
        var $input = $(document).find('input[data-field-name="reader_ps"]:visible').first();
        if ($input.length) {
            if (document.activeElement !== $input[0]) {
                $input.focus();
            }
            $input[0].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            clearInterval(timer);
        }
        if (++count >= attempts) {
            clearInterval(timer);
        }
    }, 100);
}

var ReaderPsAutoNext = basicFields.FieldChar.extend({
    events: _.extend({}, basicFields.FieldChar.prototype.events, {
        keydown: '_onKeydown',
    }),

    // FieldChar._renderEdit es síncrono (no devuelve Promise).
    _renderEdit: function () {
        var self = this;
        this._super.apply(this, arguments);
        self.$input
            .attr('autocomplete', 'off')
            .attr('data-field-name', this.name);
    },

    // Enter o Tab -> guardar línea (commit + onchange) y, tras el next_line,
    // enfocar y hacer scroll a la nueva línea (última fila).
    _onKeydown: function (ev) {
        if (ev.which === $.ui.keyCode.ENTER || ev.which === $.ui.keyCode.TAB) {
            ev.preventDefault();
            ev.stopPropagation();
            this.trigger_up('navigation_move', { direction: 'next_line' });
            focusReaderPs();
        } else {
            this._super.apply(this, arguments);
        }
    },
});

fieldRegistry.add('reader_ps_autonext', ReaderPsAutoNext);

// Al abrir el wizard: crear la fila de edición inicial (si no hay líneas) y
// enfocar el lector.
FormRenderer.include({
    _renderView: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var model = self.state && self.state.model;
            if (model && model !== 'klo.lot.reception.wizard') {
                return;
            }
            setTimeout(function () {
                var $rows = self.$el.find('tr.o_data_row');
                if (!$rows.length) {
                    var $add = self.$el.find('.o_field_x2many_list_row_add a').first();
                    if ($add.length) {
                        $add.click();
                    }
                }
                focusReaderPs();
            }, 150);
        });
    },
});

return ReaderPsAutoNext;
});
