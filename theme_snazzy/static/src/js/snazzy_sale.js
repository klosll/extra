odoo.define('theme_snazzy.custom_config', function (require) {
    'use strict';

    require('web.dom_ready');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    const dom = require('web.dom');
    var time = require('web.time');
    var portalComposer = require('portal.composer');
    const { Markup } = require('web.utils');
    var portalChatter = require('portal.chatter');
    var PortalChatter = portalChatter.PortalChatter;
    var qweb = core.qweb;
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;

    publicWidget.registry.sliderjs = publicWidget.Widget.extend({
        selector: ".o_wsale_product_page",

        start: function () {
            // accessories product slider js
            $("#snazzy_accessory_product_slider").owlCarousel({
                margin: 20,
                dots: false,
                rewind: true,
                autoPlay: 3000, //Set AutoPlay to 3 seconds
                responsiveClass: true,
                items: 3,
                loop: false,
                nav: true,
                navText: [
                    '<i class="fa fa-long-arrow-left" ></i>',
                    '<i class="fa fa-long-arrow-right" ></i>'
                ],
                responsive: {
                    0: {
                        items: 1,
                    },
                    420: {
                        items: 1,
                    },
                    768: {
                        items: 2,
                    },
                    1024: {
                        items: 3,
                    },
                    1200: {
                        items: 4,
                    },
                    1400: {
                        items: 4,
                    },
                },
            });

            // alternative product slider js
            $("#snazzy_alternative_product_slider").owlCarousel({
                margin: 20,
                dots: false,
                rewind: true,
                autoPlay: 3000, //Set AutoPlay to 3 seconds
                responsiveClass: true,
                items: 3,
                loop: false,
                nav: true,
                navText: [
                    '<i class="fa fa-long-arrow-left" ></i>',
                    '<i class="fa fa-long-arrow-right" ></i>'
                ],
                responsive: {
                    0: {
                        items: 1,
                    },
                    420: {
                        items: 1,
                    },
                    768: {
                        items: 2,
                    },
                    1024: {
                        items: 3,
                    },
                    1200: {
                        items: 4,
                    },
                    1400: {
                        items: 4,
                    },
                },
            });

            // layout3 product image
            $("#snazzy_layout3_product_image").owlCarousel({
                margin: 10,
                dots: false,
                rewind: true,
                // autoPlay: 3000, //Set AutoPlay to 3 seconds
                responsiveClass: true,
                items: 3,
                loop: false,
                nav: true,
                navText: [
                    '<i class="fa fa-long-arrow-left" ></i>',
                    '<i class="fa fa-long-arrow-right" ></i>'
                ],
                responsive: {
                    0: {
                        items: 1,
                    },
                    420: {
                        items: 1,
                    },
                    768: {
                        items: 2,
                    },
                    1024: {
                        items: 3,
                    },
                    1200: {
                        items: 4,
                    },
                    1400: {
                        items: 5,
                    },
                },
            });

            $('.product_tabs .nav-tabs li:first-child a').addClass('active show');
            $('.product_tabs .product-tab .tab-pane:first-child').addClass('active show');
            
            $.fn.isInViewport = function () {
                var elementTop = $(this).offset().top;
                var elementBottom = elementTop + $(this).outerHeight();

                var viewportTop = $(window).scrollTop();
                var viewportBottom = viewportTop + $(window).height();

                return elementBottom > viewportTop && elementTop < viewportBottom;
            };
            $('#wrapwrap').scroll(function () {
                // footer
                if ($('#product_details #o_wsale_cta_wrapper').isInViewport()) {
                    // $('.cart_visible_onscroll').removeClass('open');
                    $('.cart_product_sticky_section').removeClass('open');
                } else {
                    // $('.cart_visible_onscroll').addClass('open');
                    $('.cart_product_sticky_section').addClass('open');
                }
            });
        }
    });

    publicWidget.registry.productpageand404js = publicWidget.Widget.extend({
        selector: "#product_detail",
        events: {
            'click .product_share_buttons .snazzy_product_url_copytoclipboard': '_copyproducturltoclipboard',
            'click .product_share_buttons .open_product_share_modal': '_opensharemodal',
            'click .product_share_buttons .close_product_share_modal , .product_share_content.active': '_closesharemodal',
            'change .quantity.update_product_page_qv.second_qv': '_UpdateStickyData',
        },
        start: function () {
            var share_url = window.location.href;
            $('#snazzy_product_url').attr('value',share_url);

            // var details_height = $('#product_details').height()
            // $('div[data-image_layout="grid"] .o_wsale_product_images').css('max-height', '' + details_height + 'px');
            /*product page highlight start*/
            $('[data-toggle="popover"]').popover();
            $('body').on('click', function (e) {
                $('[data-toggle=popover]').each(function () {
                    // hide any open popovers when the anywhere else in the body is clicked
                    if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                        $(this).popover('hide');
                    }
                });
            });
            /*product page highlight end*/

            /*404 page start try inherit */
            if ($('.template_404_page').hasClass('template_404_page')) {
                $('.template_404_page').parent().siblings('hr').addClass('d-none');
            }
            /*404 page end*/
            setInterval(function () {
                $('.lazyload').lazyload();
            }, 1000);
            

            var description_height = $('.snazzy_product_description').height();
            if(description_height > 86){
                var text = $('.snazzy_product_description');
                var btn = $('.show_more_deacription');
                btn.addClass('d-block');
                btn.removeClass('d-none');
                text.animate({'height': '86px'});
                var h = text[0].scrollHeight;
                if(h > 86) {
                    btn.addClass('less');
                }
                btn.click(function(e)
                {
                    e.stopPropagation();
                    var target = $(e.target);
                    var text = $('.snazzy_product_description'),
                    btn = $(this);
                    h = text[0].scrollHeight;
                  if ($(target).hasClass('less')) {
                      $(target).removeClass('less');
                      $(target).addClass('more');
                      $(target).text('View less');
                      text.animate({'height': h});
                  }else {
                      $(target).addClass('less');
                      $(target).removeClass('more');
                      $(target).text('View more');
                      text.animate({'height': '86px'});
                  }
                });
            }

            $("#product_details > form input[name=product_id]").on('change', function(event) {
				var product_var_id = $('#product_details > form input[name=product_id]').val()
				$('#product_details > .cart_product_sticky_section .cart_product_sticky_details input[name=product_id]').val(product_var_id)
			});

        },
        _copyproducturltoclipboard: function (ev) {
            var clipboard = $(ev.currentTarget).parents(".copy_product_url").find("input").select();
            var alertmsg = $(ev.currentTarget).parents(".copy_product_url").find("input").val();          
            document.execCommand("copy");
            if ( alertmsg != "" ) {
                $( ".link_copy_successful" ).show().delay(1000).addClass('successful');               
            } 
            setTimeout(function () {
                $( ".link_copy_successful" ).removeClass('successful')
            }, 3000);
        },
        _opensharemodal: function (ev) {
            $(ev.currentTarget).parents(".product_share_buttons").find(".product_share_content").addClass('active open');
        },
        _closesharemodal: function (ev) {
            $(ev.currentTarget).parents(".product_share_buttons").find(".product_share_content").removeClass('open');
            setTimeout(function () {
                $(ev.currentTarget).parents(".product_share_buttons").find(".product_share_content").removeClass('active');
            }, 500);
        },

        _UpdateStickyData: function (ev) {
            var quantity = $(ev.currentTarget).val()
            $(".quantity.update_product_page_qv.first").val(quantity)
            $(".quantity.update_product_page_qv.first").change();
        },
        
    });

    publicWidget.registry.shoppagejs = publicWidget.Widget.extend({
        selector: ".snazzy_shop",
        events: {
            'click .price-cancel-attributes': '_pricecancelattributes',
            'click .snazzy-product-icons-toggle:not(.open)': '_productsiconanimationopen',
            'click .snazzy-product-icons-toggle.open': '_productsiconanimationclose',
        },
        start: function () {
            $('.lazyload').lazyload();
            setInterval(function () {
                $(".product_extra_hover_image").hover(function (ev) {
                    var product_id = $(ev.currentTarget).find('.has_extra_hover_image .extra_hover_image').attr('productid');
                    var target_image = $(ev.currentTarget).find('.has_extra_hover_image .extra_hover_image img');
                    $(target_image).addClass('h-100').attr('data-src', '/web/image/product.template/' + product_id + '/hover_image');
                    $('.lazyload').lazyload();
                }, function (ev) {
                    var target_image = $(ev.currentTarget).find('.has_extra_hover_image .extra_hover_image img');
                    $(target_image).delay(200).attr('data-src', ' ');
                });
            }, 1000);

            // Price slider code start --- shoppage
		    var minval = $("input#m1").attr('value'),
                maxval = $('input#m2').attr('value'),
                minrange = $('input#ra1').attr('value'),
                maxrange = $('input#ra2').attr('value'),
                website_currency = $('input#snazzy_website_currency').attr('value');
            if (!minval) {
                minval = 0;
            }
            if (!maxval) {
                maxval = maxrange;
            }
            if (!minrange) {
                minrange = 0;

            }
            if (!maxrange) {
                maxrange = 2000;
            }

            $("div#priceslider").ionRangeSlider({
                keyboard: true,
                min: parseInt(minrange),
                max: parseInt(maxrange),
                type: 'double',
                from: minval,
                skin: "square",
                to: maxval,
                step: 1,
                prefix: website_currency,
                grid: true,
                onFinish: function(data) {
                    $("input[name='min1']").attr('value', parseInt(data.from));
                    $("input[name='max1']").attr('value', parseInt(data.to));
                    $("div#priceslider").closest("form").submit();
                },
            });
            // Price slider code end --- shoppage

            var size = $(window).width();
            if (size <= 767) {
                $(function () {
                    if ($(".snazzy_shop #products_grid").hasClass("o_wsale_layout_list")) {
                        $(".snazzy_shop #products_grid").removeClass("o_wsale_layout_list");
                    }
                });
            }

            $('.active_attributes .cancel-attributes').on('click', function(){
                var attr_val = $(this).attr('id')
                var input_data = ($('form.js_attributes input[value="'+attr_val+'"]') || $('.brand-c input[value="'+attr_val+'"]'))
                var option_data = $('form.js_attributes option[value="'+attr_val+'"]')
                $(input_data).click();
                if($(option_data).val() == attr_val){
                    var trigger_val = $(option_data).parent().val('');
                    $(trigger_val).change();
                } 
            })

            $('.search_filter_attributes').keyup(function(e){
                if (e.which == 13) e.preventDefault();
                var input_val = $(this).val()
                var loop_el = $(this).parent().find('li,.list-group-item,.css_attribute_color,.brand_content')
             
                $(loop_el).each(function(index){
                    var label_text = $(this).find('.get_attribute_name').text()
                    var brand_id = $(this).find('.brand_image').attr('id')
    
                    if (String(label_text).toLowerCase().match(input_val.toLowerCase()) || String(brand_id).toLowerCase().match(input_val.toLowerCase()) ) {
                        $(this).removeClass('d-none')
                    }else{
                        $(this).addClass('d-none')
                    }
                })
            })
            
            
            var size = $(window).width();
            if (size <= 991) {
                var list_height = $('#o_wsale_offcanvas_categories .category-height-overflow').height();
            }
            else{
                var list_height = $('.category-height-overflow').height();
            }
            
            if(list_height > 60){
                if (size <= 991) {
                    var text = $('#o_wsale_offcanvas_categories .category-height-overflow');
                }
                else{
                    var text = $('.category-height-overflow');
                }
                var btn = $('.show-more-btn');
                var h = text[0].scrollHeight;
                if(h > 60) {
                    btn.addClass('less');
                    btn.css('display', 'block');
                }
          
                btn.click(function(e)
                {
                    e.stopPropagation();
                    var target = $(e.target);
                   
                    if (size <= 991) {
                        var text = $('#o_wsale_offcanvas_categories .category-height-overflow');
                    }
                    else{
                        var text = $('.category-height-overflow');
                    }
                    btn = $(this);
                    h = text[0].scrollHeight;
              
                    if (size <= 991) {
                        if ($(target).hasClass('less')) {
                            $(target).removeClass('less');
                            $(target).addClass('more');
                            $(target).text('- View less');
                            text.animate({'height': '186px'});
                        }else {
                            $(target).addClass('less');
                            $(target).removeClass('more');
                            $(target).text('+ View more');
                            text.animate({'height':h});
                        }
                    }
                    else{
                        if ($(target).hasClass('less')) {
                            $(target).removeClass('less');
                            $(target).addClass('more');
                            $(target).text('- View less');
                            text.animate({'height':h});
                        }else {
                            $(target).addClass('less');
                            $(target).removeClass('more');
                            $(target).text('+ View more');
                            text.animate({'height':'186px'});
                        }
                    }
                  
                });
            }
        },
        _pricecancelattributes: function () {
            var minprice = $('#products_grid_before #o_wsale_price_range_option input[type="range"]').attr('min');
            var maxprice = $('#products_grid_before #o_wsale_price_range_option input[type="range"]').attr('max');
            $('#products_grid_before #o_wsale_price_range_option input[type="range"]').attr('value', minprice+','+maxprice);
            $('form.js_attributes').submit();
        },
        _productsiconanimationopen: function (ev) {
            $(ev.currentTarget).parents('#products_grid').find('.snazzy-product-icons-toggle').removeClass('open')
            $(ev.currentTarget).addClass('open')
        },
        _productsiconanimationclose: function (ev) {
            $(ev.currentTarget).removeClass('open')
        },
    });

    // Review Publish Date Formate
    PortalChatter.extend({
        preprocessMessages(messages) {
            _.each(messages, function (m) {
                m['author_avatar_url'] = _.str.sprintf('/web/image/%s/%s/author_avatar/50x50', 'mail.message', m.id);
                m['published_date_str'] = _.str.sprintf(_t('Published on %s'), moment(time.str_to_datetime(m.date)).format('MM Do YYYY, h:mm:ss a'));
                m['body'] = Markup(m.body);
            });
            return messages;
        },
    });
});