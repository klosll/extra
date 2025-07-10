odoo.define('theme_snazzy.icon_pack', function (require) {
	'use strict';
	
		require('web_editor.rte.summernote');
		var icofonts = require('wysiwyg.fonts');
		var faIconWidget = require('wysiwyg.widgets.media').IconWidget;
		var core = require('web.core');
		var _t = core._t;
		var dom = $.summernote.core.dom;
		var eventHandler = $.summernote.eventHandler;
		var fn_attach = eventHandler.attach;
	
		icofonts.fontIcons.push({base: 'lnr', parser: /\.(lnr-(?:\w|-)+)::?before/i});
		icofonts.fontIcons.push({base: 'icon', parser: /\.(icon-(?:\w|-)+)::?before/i});
		icofonts.fontIcons.push({base: 'icofont', parser: /\.(icofont-(?:\w|-)+)::?before/i});
		icofonts.fontIcons.push({base: 'lni', parser: /\.(lni-(?:\w|-)+)::?before/i});
		icofonts.fontIcons.push({base: 'ri', parser: /\.(ri-(?:\w|-)+)::?before/i});
		icofonts.fontIcons.push({base: 'ti', parser: /\.(ti-(?:\w|-)+)::?before/i});
	
		faIconWidget.include({
			save: function() {
				var lnrf = "{base: 'lnr', font: ''}"
				var iconf = "{base: 'icon', font: ''}"
				var icofontf = "{base: 'icofont', font: ''}"
				var lnif = "{base: 'lni', font: ''}"
				var rif = "{base: 'ri', font: ''}"
				var tif = "{base: 'ti', font: ''}"
	
				var iconFont = this._getFont(this.selectedIcon) || {base: 'fa', font: ''} || lnrf || iconf || icofontf || lnif || rif || tif;
	
				console.log('iconFont.base', iconFont.base)
				console.log('this', this)
				if (iconFont.base = "lnr"){
					this.$media.removeClass("icon icofont lni ri ti fa")
				}
				if (iconFont.base = "icon"){
					this.$media.removeClass("lnr icofont lni ri ti fa")
				}
				if (iconFont.base = "icofont"){
					this.$media.removeClass("icon lnr lni ri ti fa")
				}
				if (iconFont.base = "lni"){
					this.$media.removeClass("icon icofont lnr ri ti fa")
				}
				if (iconFont.base = "ri"){
					this.$media.removeClass("icon icofont lni lnr ti fa")
				}
				if (iconFont.base = "ti"){
					this.$media.removeClass("icon icofont lni ri lnr fa")
				}
				if (iconFont.base = "fa"){
					this.$media.removeClass("icon icofont lni ri ti lnr")
				}
				return this._super.apply(this,arguments);
			}
		})
		
		eventHandler.attach = function (oLayoutInfo, options) {
			fn_attach.call(this, oLayoutInfo, options);
	
			create_dblclick_feature("span.lnr, i.lnr, span.icon, i.icon, span.icofont, i.icofont, span.lni, i.lni, span.ri, i.ri, span.ti, i.it", function () {
				eventHandler.modules.imageDialog.show(oLayoutInfo);
			});
			/* odoo default function overide*/
			function create_dblclick_feature(selector, callback) {
				var show_tooltip = true;
	
				oLayoutInfo.editor().on("dblclick", selector, function (e) {
					var $target = $(e.target);
					if (!dom.isContentEditable($target)) {
						// Prevent edition of non editable parts
						return;
					}
	
					show_tooltip = false;
					callback();
					e.stopImmediatePropagation();
				});
	
				oLayoutInfo.editor().on("click", selector, function (e) {
					var $target = $(e.target);
					if (!dom.isContentEditable($target)) {
						// Prevent edition of non editable parts
						return;
					}
	
					show_tooltip = true;
					setTimeout(function () {
						// Do not show tooltip on double-click and if there is already one
						if (!show_tooltip || $target.attr('title') !== undefined) {
							return;
						}
						$target.tooltip({title: _t('Double-click to edit'), trigger: 'manuel', container: 'body'}).tooltip('show');
						setTimeout(function () {
							$target.tooltip('dispose');
						}, 800);
					}, 400);
				});
			}
		};
	
	});