odoo.define('theme_snazzy.wishlist_page', function (require) {

    var publicWidget = require('web.public.widget');
    require('website_sale_wishlist.wishlist');

    publicWidget.registry.ProductWishlist.include({
        
        events: _.extend({}, publicWidget.registry.ProductWishlist.prototype.events || {}, {
            'click .wishlist_product_select_all': '_select_all',
            'click .wishlist_product_remove_selected': '_remove_selected',
            'click .wishlist_product_add_selected_to_cart': '_add_selected_to_cart',
            'click .wishlist_product_add_all_to_cart': '_add_all_to_cart',
            'click #remove_to_wishlist_button': '_remove_to_wishlist_button',
            'click .form-check-input': '_show_btn_on_check_input',
        }),
        willStart: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var wishDef;
            if (this.wishlistProductIDs.length != +$('header .my_wish_quantity').text()) {
                wishDef = $.get('/shop/wishlist', {
                    count: 1,
                }).then(function (res) {
                    self.wishlistProductIDs = JSON.parse(res);
                    sessionStorage.setItem('website_sale_wishlist_product_ids', res);
                });
    
            }
            return Promise.all([def, wishDef]);
        },
        _show_btn_on_check_input: function(){
            var checkedRadio = this.$('.wishlist-section tbody input[type="checkbox"]:checked');
            if (checkedRadio.length > 0){
                $('.form-check-input').parents('#snazzy_wishlist_page_section').find('.wishlist_product_remove_selected').removeClass('d-none');
                $('.form-check-input').parents('#snazzy_wishlist_page_section').find('.wishlist_product_add_selected_to_cart').removeClass('d-none');
            } else {
                $('.form-check-input').parents('#snazzy_wishlist_page_section').find('.wishlist_product_remove_selected').addClass('d-none');
                $('.form-check-input').parents('#snazzy_wishlist_page_section').find('.wishlist_product_add_selected_to_cart').addClass('d-none');
            }
        },

        _select_all: function () {
            if($('.form-check-input').prop("checked") == true){
                $('tbody .form-check-input').prop('checked', true).attr('checked', 'checked');
            }
            else {
                $('tbody .form-check-input').prop('checked', false).removeAttr('checked');
            }
        },

        _onClickWishAdd: function (ev) {
            var self = this;
            this._addOrMoveWish(ev).then(function () {
                self.$('.wishlist-section .o_wish_add').removeClass('disabled');
            });
        },

        _remove_selected: function (ev) {
            $('.form-check-input:checked').parents('tr').find('.o_wish_rm').addClass('product_remove');
            $(ev.currentTarget).parents('.wishlist-section').find('.product_remove').click();
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_page_toast').addClass("show").fadeIn().delay(2000).fadeOut();
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').removeClass("add_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').addClass("remove_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_toast_text_content').text("Product remove from wishlist");
        },

        _add_selected_to_cart: function (ev) {
            $('.form-check-input:checked').parents('tr').find('.o_wish_add').addClass('product_add');
            $(ev.currentTarget).parents('.wishlist-section').find('.product_add').click()
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_page_toast').addClass("show").fadeIn().delay(2000).fadeOut();
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').removeClass("remove_product")
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').addClass("add_product")
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_toast_text_content').text("Product added to cart")
        },

        _add_all_to_cart: function (ev) {
            $(ev.currentTarget).parents('.wishlist-section').find('.o_wish_add').click();
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_page_toast').addClass("show").fadeIn().delay(2000).fadeOut();
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').removeClass("remove_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').addClass("add_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_toast_text_content').text("All products added to cart");
        },

        _remove_to_wishlist_button: function (ev) {
            $(ev.currentTarget).parents('tr').find('input[type="checkbox"]:checked').click();
            this._removeWish(ev, false);
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_page_toast').addClass("show").fadeIn().delay(2000).fadeOut();
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').removeClass("add_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.toast-body').addClass("remove_product");
            $(ev.currentTarget).parents('.wishlist-section').find('.wishlist_toast_text_content').text("Product removed from wishlist");
        },
    })    
})
