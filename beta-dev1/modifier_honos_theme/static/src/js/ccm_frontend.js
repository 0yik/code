odoo.define('modifier_honos_theme.ccm_frontend_js', function(require) {
    'use strict';

    var animation = require('web_editor.snippets.animation');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var wish = require('wishlist.wish');
    var _t = core._t;
    
    // for homepage block
    animation.registry.top_banner_slider = animation.Class.extend({
        selector: ".top_banner_slider",
        start: function(editable_mode) {
        	var self = this;
            if (editable_mode) {
                $('.top_banner_slider').empty().append('<div class="container">\
                        <div class="block-title">\
                        <h3 class="fancy" style="text-align: center;">Top Banner Block</h3>\
                    </div>\
                </div>')
            }
            if (!editable_mode) {
                ajax.jsonRpc("/modifier_honos_theme/top_banner_dynamic_slider", 'call', {
                  }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".top_banner_slider").removeClass('hidden');
                        $('#slide div.item').first().addClass('active');
                        //$('#slide a.right').trigger("click");
                        //$('#booked_buy, #booked_buy2, #booked_buy3').click(function(){
                        	/*var warn_popup = $(this).parent().find("#warning");
                        	warn_popup.dialog({
    							modal: true,
    							autoOpen: false,
    							title: _t("IMPORTANT!"),
    							minHeight: 170,
    							maxHeight: 170,
    							height: 170,
    							width: 400,
    							open: function() {
    								$('.ui-widget-overlay').bind('click', function() {
    									warn_popup.dialog('close');
    								})
    							}
    						});
                        	warn_popup.dialog('open');*/
                        //});
                    }
                });
            }
        }
    });
    
    animation.registry.new_arrivals = animation.Class.extend({
        selector: ".arrival_slider",
        start: function(editable_mode) {
        	var self = this;
            if (editable_mode) {
                $('#new_arrival').empty();
            }
            if (!editable_mode) {
                ajax.jsonRpc("/modifier_honos_theme/new_arrival_dynamic_slider", 'call', {
                  }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".arrival_slider").removeClass('hidden');
                        self.$target.find("#owl-new_arrival").owlCarousel({
            			    items : 4, //10 items above 1000px browser width
            			    itemsDesktop : [1000,5], //5 items between 1000px and 901px
            			    itemsDesktopSmall : [900,5], // betweem 900px and 601px
            			    itemsTablet: [600,4], // items between 600 and 421px
            			    itemsMobile : [420,3], // itemsMobile disabled - inherit from itemsTablet option,
            			    loop:true,
                    		margin:10,
                    		autoPlay:true,
                    		autoPlayTimeout:1000,
                    		autoPlayHoverPause:true,
            			});
                    }
                    wish.getwishproduct()
	          		var SCW=self.$target.find(".add2wish_SC")
	          		SCW.click(function() {
	  					// For Loading Icon
	  					$('.cus_theme_loader_layout').removeClass('hidden');
	  					var pid = $(this).attr('data-id');
	  					wish.getwish(pid)
	      			})
                });
            }
        }
    });
    animation.registry.featured_prod_categories = animation.Class.extend({
        selector: ".custom_js_get_category",
        start: function(editable_mode) {
        	var self = this;
            if (editable_mode) {
                $('#all_categ').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-categ-slider-type');
                ajax.jsonRpc("/modifier_honos_theme/main_category_dynamic_slider", 'call', {
                  }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".custom_js_get_category").removeClass('hidden');
                        self.$target.find("#owl-fcat").owlCarousel({
            			    items : 4, //10 items above 1000px browser width
            			    itemsDesktop : [1000,5], //5 items between 1000px and 901px
            			    itemsDesktopSmall : [900,5], // betweem 900px and 601px
            			    itemsTablet: [600,4], // items between 600 and 421px
            			    itemsMobile : [420,3], // itemsMobile disabled - inherit from itemsTablet option,
            			    loop:true,
                    		margin:10,
                    		autoPlay:true,
                    		autoPlayTimeout:1000,
                    		autoPlayHoverPause:true,
            			});
                    }
                });
            }
        }
    });
    // end of homepage block
    
    /* dynamic featured categories code*/
    animation.registry.featured_categories = animation.Class.extend({
        selector: ".oe_multi_category_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_ccm_featured_categories').empty();
                var name = _t("Multi Purpose Featured Products Slider")
                $('#theme_ccm_featured_categories').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-cat-slider-type');
                $.get("/modifier_honos_theme/category_dynamic_slider", {
                    'slider-type': slider_type || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_category_slider").removeClass('hidden');
                        self.$target.find("#owl-fp").owlCarousel({
            			    items : 4, //10 items above 1000px browser width
            			    itemsDesktop : [1000,5], //5 items between 1000px and 901px
            			    itemsDesktopSmall : [900,5], // betweem 900px and 601px
            			    itemsTablet: [600,4], // items between 600 and 421px
            			    itemsMobile : [420,3], // itemsMobile disabled - inherit from itemsTablet option,
            			    loop:true,
                    		margin:10,
                    		autoPlay:true,
                    		autoPlayTimeout:1000,
                    		autoPlayHoverPause:true,
            			});
                    }
                });
            }
        }
    });
    
    
    /* dynamic featured New Arrival products code*/
    animation.registry.new_arrival = animation.Class.extend({
        selector: ".oe_multi_arrival_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_ccm_new_arrival').empty();
                var name = _t("Multi Purpose New Arrival products Slider")
                $('#theme_ccm_new_arrival').empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + name + '</h3>\
                                                    </div>\
                                                </div>')
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-arrival-slider-type');
                $.get("/modifier_honos_theme/arrival_dynamic_slider", {
                    'slider_arrival_type': slider_type || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_arrival_slider").removeClass('hidden');
                        self.$target.find("#owl-na").owlCarousel({
            			    items : 4, //10 items above 1000px browser width
            			    itemsDesktop : [1000,5], //5 items between 1000px and 901px
            			    itemsDesktopSmall : [900,5], // betweem 900px and 601px
            			    itemsTablet: [600,4], // items between 600 and 421px
            			    itemsMobile : [420,3], // itemsMobile disabled - inherit from itemsTablet option,
            			    loop:true,
                    		margin:10,
                    		autoPlay:true,
                    		autoPlayTimeout:1000,
                    		autoPlayHoverPause:true,
            			});
                    }
                });
            }
        }
    });
});