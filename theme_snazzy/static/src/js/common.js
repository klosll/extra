odoo.define('theme_snazzy.common', function (require) {
  'use strict';

  require('web.dom_ready');
  var publicWidget = require('web.public.widget');
  var core = require('web.core');
  var ajax = require('web.ajax');
  var rpc = require('web.rpc');
  var _t = core._t;


  var publicWidget = require('web.public.widget');

  publicWidget.registry.loginformjs = publicWidget.Widget.extend({
    selector: ".oe_login_form,.login-modal",

    events: {
      'click .toggle-password': '_toggle_password_fn',
    },

    _toggle_password_fn: function () {

      $(this).toggleClass("fa-eye fa-eye-slash");
      var input = $($(this).attr("toggle"));

      if ($('input#password').attr("type") == "password") {
        $('input#password').attr('type', 'text');
      } 
      else {
        $('input#password').attr('type', 'password');
      } 
    },
  });

})

/* header category menu --- submenu*/
$(function() {
  var categ_target = $(".snazzy-header-category > li.dropdown-submenu > .nav-link > i.ti");
  var parent_categ = $(categ_target).parent().parent();
  if ($(categ_target).hasClass("ti")) {
      $(parent_categ).addClass('dropend');
  }
});
   

$(function() {
  $("body").addClass("blured-bg");
  /* cart sidebar js */
  $(document).on("click", function(e) {
    // if (!$(e.target).closest('#cart_sidebar').length) {
    //   $("#cart_sidebar.toggled").parents(".blured-bg").addClass("active");
    //   $("#cart_sidebar").removeClass("toggled");
    // }
  });
  /* category sidebar js */
  $(".filter_btn").on("click", function(e) {
    $("category-sidebar").parents(".blured-bg").addClass("active");
    $(".category-sidebar").addClass("toggled");
    e.stopPropagation()
  });
  // $(".bottom_bar_filter_button").on("click", function(e) {
  //   $("category-sidebar").parents(".blured-bg").addClass("active");
  //   $(".category-sidebar").addClass("toggled");
  //   e.stopPropagation()
  // });
  $("#category_close").on("click", function(e) {
    $("category-sidebar").parents(".blured-bg").removeClass("active");
    $(".category-sidebar").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('.category-sidebar').length) {
      $(".category-sidebar.toggled").parents(".blured-bg").removeClass("active");
      $(".category-sidebar").removeClass("toggled");
    }

    if (!$(e.target).closest('.bizople-search-results').length) {
      $(".bizople-search-results").hide("dropdown-menu");
    }
    if (!$(e.target).closest('.bizople-search-text').length) {
      $(".bizople-search-text").hide("dropdown-menu");
    }
  });
  $("#categbtn-popup,#categbtn").on("click", function(e) {
    $(".bizople-search-results").hide("dropdown-menu");
    $(".bizople-search-text").hide("dropdown-menu");
  });
});

