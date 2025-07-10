odoo.define('theme_snazzy.store_location_data', function (require) {
    'use strict';

    require('web.dom_ready');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;


    var publicWidget = require('web.public.widget');

    publicWidget.registry.store_location_data = publicWidget.Widget.extend({
        selector: ".store",
        events: {
            'click .radio_delivery': 'check_delivery',
            'click .radio_pickup': 'check_pickup',
            // 'click .store-list': 'check_store',
            'click input[name=pickup_address]': 'check_store',
        },

        start: function () {
            var default_select = this.$el.find(".radio_delivery").is(":checked");
            if (default_select == true) {
                this.check_delivery()
            }
        },

        check_delivery: function () {
            $('.checkout_main .bill-check .row').removeClass('d-none')
            $('.store_data').addClass('d-none')
            $('#wrap').removeClass('checkout_btn_disable');
            $('.store_menu li').css('box-shadow','')
            $('.store_menu li').find('#store_list_id').removeClass('selected')
            this.check_store()
        },

        check_pickup: function () {
            $('#wrap').addClass('checkout_btn_disable');
            $('.checkout_main .bill-check .row').addClass('d-none')
            $('.store_data').removeClass('d-none')
            $('.store_line .row').each(function () {
                if ($(this).find("input[name='pickup_address']").is(':checked')) {
                    $('#wrap').removeClass('checkout_btn_disable');
                }
            });
        },

        check_store: function () {
            if($(".radio_pickup").is(":checked")){
                $('.store_line .row .store-data').each(function () {
                    if ($(this).find("input[name='pickup_address']").is(':checked')) {
                        $('#wrap').removeClass('checkout_btn_disable')
                        var store_id = $(this).find("input[name='info_id']").attr('value');
                        if (store_id) {
                            ajax.rpc('/add_store_data', {
                                'store_id': store_id
                            })
                        }
                    }
                })
            }
            else{
                ajax.rpc('/add_store_data', {
                    'store_id': false
                })
            }
        }
    });
});
