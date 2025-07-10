odoo.define('product_reference_generator_bizople.sale_product', function(require) {

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');
    var _t = core._t;
    publicWidget.registry.WebsiteSale.include({
        onChangeVariant: function (ev) {
            this._super.apply(this, arguments);
            var $parent = $(ev.target).closest('.js_product');
            var qty = $parent.find('input[name="add_qty"]').val();
            var combination = this.getSelectedVariantValues($parent);
            var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
            var productTemplateId = parseInt($parent.find('.product_template_id').val());
            return ajax.jsonRpc('/product_code/get_combination_info', 'call', {
                'product_template_id': productTemplateId,
                'product_id': this._getProductId($parent),
                'combination': combination,
                'add_qty': parseInt(qty),
                'pricelist_id': this.pricelistId || false,
                'parent_combination': parentCombination,
            }).then(function (data) {
                if (data){
                    $('.product_internal_reference').html(data)
                    $('.product_internal_reference').removeClass('d-none');
                } else {
                    $('.product_internal_reference').addClass('d-none');
                }
                // $('.product_ref_code').html(data)
            });

        }
    })    
})

// ajax cart modal js start

odoo.define('theme_snazzy.ajax_cart', function(require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');
    var timeout;
    var _t = core._t;
    var wSaleUtils = require('website_sale.utils');

    publicWidget.registry.WebsiteSale.include({
        _onClickSubmit: function (ev, forceSubmit) {
            
            var self = this
            var type_add = "add"

            if ($(ev.currentTarget).is('#add_to_cart, #products_grid .a-submit:not(.ajax-cart-btn)') && !forceSubmit) {
                // self._add_to_cart_button_toast()
                return;
            }
            var $aSubmit = $(ev.currentTarget);
            if (!$aSubmit.is(".disabled")) {
                ev.preventDefault();
                if ($aSubmit.parents('.ajax_cart_modal_tools').length) {
                    var frm = $aSubmit.closest('form');
                    var product_product = frm.find('input[name="product_id"]').val();
                    var quantity = frm.find('.quantity').val();
                    if(!quantity) {
                       quantity = 1;
                    }
                    ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'add_qty':quantity}).then(function(data) {
                        if(data) {
                            sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
                            $(".my_cart_quantity")
                            .parents('li.o_wsale_my_cart').removeClass('d-none').end()
                            .addClass('o_mycart_zoom_animation').delay(300)
                            .queue(function () {
                                $(this)
                                .toggleClass('fa fa-warning', !data.cart_quantity)
                                .text(data.cart_quantity || '')
                                .removeClass('o_mycart_zoom_animation')
                                .dequeue();
                            });
                            // self._add_to_cart_button_toast(type_add)
                        }
                    });
                    setTimeout(function () {
                        $(".select-modal-backdrop").remove();
                        $(".select-modal").remove();
                        $(".quick-modal-backdrop").remove();
                        $(".quick-modal").remove();
                    }, 1000);
                } else {
                    $aSubmit.closest('form').submit();
                    // self._add_to_cart_button_toast(type_add)
                }
            }
            if ($aSubmit.hasClass('a-submit-disable')){
                $aSubmit.addClass("disabled");
                // self._add_to_cart_button_toast()
            }
            if ($aSubmit.hasClass('a-submit-loading')){
                var loading = '<span class="fa fa-cog fa-spin"/>';
                var fa_span = $aSubmit.find('span[class*="fa"]');
                if (fa_span.length){
                    fa_span.replaceWith(loading);
                } else {
                    $aSubmit.append(loading);
                }
            }
        },

        _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
            var self = this

            _.each($dom_optional, function (elem) {
                $(elem).find('.js_quantity').text(value);
                productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);
    
            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: parseInt($input.data('product-id'), 10),
                    set_qty: value
                },
            }).then(function (data) {
                $input.data('update_change', false);
                var check_value = parseInt($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger('change');
                    return;
                }
                sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
                if (!data.cart_quantity) {
                    return window.location = '/shop/cart';
                }
                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).text(data.quantity);
    
                wSaleUtils.updateCartNavBar(data);
                wSaleUtils.showWarning(data.warning);
                // Propagating the change to the express checkout forms
                core.bus.trigger('cart_amount_changed', data.amount, data.minor_amount);

                self._rpc({
                    route: "/update/cartsidebar",
                }).then(function (data) {
                    $("#wrapwrap #cart_sidebar .cart-content").first().before(data).end().remove();
                });
            });
        },
    });

    // publicWidget.registry.accesorycart.include({
    publicWidget.registry.accesorycart = publicWidget.Widget.extend({
        selector: '.alternative_and_accessory_products',
        events:{
            "click .js_add_accesory_products":"_acccart"
        },
        _acccart: function (ev) {
            $(ev.currentTarget).prev('input').val(1).trigger('change');
        },
    });
});

// ajax cart modal js ends