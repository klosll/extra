odoo.define('theme_snazzy.bizcommon_editor_js', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var snippetsEditor = require('web_editor.snippet.editor');

    // stop saving the dynamic content of the configurator in edit mode start
    options.registry.oe_cat_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".oe_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },
        cleanForSave: function() {
            $('.bizople_dynamic_config_tool [class*=container]').empty();
        },
    })
    // stop saving the dynamic content of the configurator in edit mode end
});