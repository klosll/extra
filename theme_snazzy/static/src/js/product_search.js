odoo.define("theme_snazzy.product_search", function (require) {
    "use strict";
    
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.snazzySearchBar = publicWidget.Widget.extend({
        selector : '.bizople-search, .search-box',
        events: {
            "keyup .search-query-bizople": "_onKeydown",
            "click .search-categ .select-category":"_changeCategory"
        },
        init: function () {
            this._super.apply(this, arguments);
    
            this._onKeydown = _.debounce(this._onKeydown, 400);
        },
    
        _onKeydown: function(ev) {
            var search_var = $(ev.currentTarget).val()
            $.get("/snazzy/search/product", {
                'category':$("#tvsearchCateg").val(),
                'term': search_var,
           }).then(function(data){
                if(data){
                    $(".bizople-search .bizople-search-results").remove()
                    $(".bizople-search .bizople-search-text").remove()
                    $('.bizople-search .o_wsale_search_order_by').after(data)
                    $(".search-box .bizople-search-results").remove()
                    $(".search-box .bizople-search-text").remove()
                    $('.search-box .o_wsale_search_order_by').after(data)
                }
    
            });
        },
        _changeCategory:function(ev){
            var getcatid = $(ev.currentTarget).attr("data-id");
            var getcatname = $(ev.currentTarget).text().trim();
            $("#tvsearchCateg").val(getcatid);
            $("#categbtn > .categ-name").text(getcatname);
            $(".select-category").removeClass("text-primary");
            $(ev.currentTarget).addClass("text-primary");
        },
    });
});