odoo.define('modifier_honos_theme.ccm_quick_view', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var ajax = require('web.ajax');
    var utils = require('web.utils');
    var core = require('web.core');
    var _t = core._t;

    if(!$('.oe_website_sale').length) {
        return $.Deferred().reject("DOM doesn't contain '.oe_website_sale'");
    }

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        $(oe_website_sale).on("change", 'input[name="add_qty"]', function (event) {
            var product_ids = [];
            var product_dom = $(".js_product .js_add_cart_variants[data-attribute_value_ids]").last();
            if (!product_dom.length) {
                return;
            }
            _.each(product_dom.data("attribute_value_ids"), function(entry) {
                product_ids.push(entry[0]);});
            var qty = $(event.target).closest('form').find('input[name="add_qty"]').val();

            if ($("#product_detail").length) {
                // display the reduction from the pricelist in function of the quantity
                ajax.jsonRpc("/shop/get_unit_price", 'call', {'product_ids': product_ids,'add_qty': parseInt(qty)})
                .then(function (data) {
                    var current = product_dom.data("attribute_value_ids");
                    for(var j=0; j < current.length; j++){
                        current[j][2] = data[current[j][0]];
                    }
                    product_dom.attr("data-attribute_value_ids", JSON.stringify(current)).trigger("change");
                });
            }
        });

        // change for css
        $(oe_website_sale).on('mouseup touchend', '.js_publish', function (ev) {
            $(ev.currentTarget).parents(".thumbnail").toggleClass("disabled");
        });

        var clickwatch = (function(){
              var timer = 0;
              return function(callback, ms){
                clearTimeout(timer);
                timer = setTimeout(callback, ms);
              };
        })();

        $(oe_website_sale).on("change", ".oe_cart input.js_quantity[data-product-id]", function () {
          var $input = $(this);
            if ($input.data('update_change')) {
                return;
            }
          var value = parseInt($input.val() || 0, 10);
          var $dom = $(this).closest('tr');
          //var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
          var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
          var line_id = parseInt($input.data('line-id'),10);
          var product_ids = [parseInt($input.data('product-id'),10)];
          clickwatch(function(){
            $dom_optional.each(function(){
                $(this).find('.js_quantity').text(value);
                product_ids.push($(this).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);

            ajax.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': line_id,
                'product_id': parseInt($input.data('product-id'), 10),
                'set_qty': value
            }).then(function (data) {
                $input.data('update_change', false);
                if (value !== parseInt($input.val() || 0, 10)) {
                    $input.trigger('change');
                    return;
                }
                var $q = $(".my_cart_quantity");
                if (data.cart_quantity) {
                    $q.parents('li:first').removeClass("hidden");
                }
                else {
                    $q.parents('li:first').addClass("hidden");
                    $('a[href^="/shop/checkout"]').addClass("hidden");
                }

                $q.html(data.cart_quantity).hide().fadeIn(600);
                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);

                $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();

                if (data.warning) {
                    var cart_alert = $('.oe_cart').parent().find('#data_warning');
                    if (cart_alert.length === 0) {
                        $('.oe_cart').prepend('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">'+
                                '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning + '</div>');
                    }
                    else {
                        cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning);
                    }
                    $input.val(data.quantity);
                }
            });
          }, 500);
        });

    
        // hack to add and remove from cart with json
        $(oe_website_sale).on('click', 'a.js_add_cart_json', function (ev) { 
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.parent().find("input");
            var product_id = +$input.closest('*:has(input[name="product_id"])').find('input[name="product_id"]').val();
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val() || 0, 10);
            // if they are more of one input for this product (eg: option modal)
            $('input[name="'+$input.attr("name")+'"]').add($input).filter(function () {
                var $prod = $(this).closest('*:has(input[name="product_id"])');
                return !$prod.length || +$prod.find('input[name="product_id"]').val() === product_id;
            }).val(quantity > min ? (quantity < max ? quantity : max) : min);
            $input.change();
            return false;
        });
        
        $('.oe_website_sale .a-submit, #comment .a-submit').off('click').on('click', function (event) {
            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
                $(this).closest('form').submit();
            }
        });
        $('form.js_attributes input, form.js_attributes select', oe_website_sale).on('change', function (event) {
            if (!event.isDefaultPrevented()) {
                $(this).closest("form").submit();
            }
        });

        // change price when they are variants
        $('form.js_add_cart_json label', oe_website_sale).on('mouseup touchend', function () {
            var $label = $(this);
            var $price = $label.parents("form:first").find(".oe_price .oe_currency_value");
            if (!$price.data("price")) {
                $price.data("price", parseFloat($price.text()));
            }
            var value = $price.data("price") + parseFloat($label.find(".badge span").text() || 0);

            var dec = value % 1;
            $price.html(value + (dec < 0.01 ? ".00" : (dec < 1 ? "0" : "") ));
        });
        // hightlight selected color
        $('.css_attribute_color input', oe_website_sale).on('change', function () {
            $('.css_attribute_color').removeClass("active");
            $('.css_attribute_color:has(input:checked)').addClass("active");
        });

        function price_to_str(price) {
            var l10n = _t.database.parameters;
            var precision = 2;

            if ($(".decimal_precision").length) {
                precision = parseInt($(".decimal_precision").last().data('precision'));
            }
            var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
            formatted[0] = utils.insert_thousand_seps(formatted[0]);
            return formatted.join(l10n.decimal_point);
        }

        function update_product_image(event_source, product_id) { 
            if ($('#o-carousel-product').length) {
                var $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img');
                $img.attr("src", "/web/image/product.product/" + product_id + "/image");
                $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                    .data('oe-model', 'product.product').data('oe-id', product_id);

                $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img_small');
                if ($img) { // if only one, thumbnails are not displayed
                    $img.attr("src", "/web/image/product.product/" + product_id + "/image/90x90");
                    $('.carousel').carousel(0);
                }
            }
            else {
                var $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
                $img.attr("src", "/web/image/product.product/" + product_id + "/image");
                $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                    .data('oe-model', 'product.product').data('oe-id', product_id);
            }
        }
    	
        $(oe_website_sale).on('change', 'input.js_product_change', function () { 
            var self = this;
            var $parent = $(this).closest('.js_product');
            $.when(base.ready()).then(function() {
                $parent.find(".oe_default_price:first .oe_currency_value").html( price_to_str(+$(self).data('lst_price')) );
                $parent.find(".oe_price:first .oe_currency_value").html(price_to_str(+$(self).data('price')) );
            });
            update_product_image(this, +$(this).val());
        });
  
        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
        	var $ul = $(ev.target).closest('.js_add_cart_variants');
            var $parent = $ul.closest('.js_product');
            var $product_id = $parent.find('input.product_id').first();
            var $price = $parent.find(".oe_price:first .oe_currency_value");
            var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
            var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
            var variant_ids = $ul.data("attribute_value_ids");
            var values = [];
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                values.push(+$(this).val());
            });

            $parent.find("label").removeClass("text-muted css_not_available");

            var product_id = false;
            var prod_qty = false;
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    $.when(base.ready()).then(function() {
                        $price.html(price_to_str(variant_ids[k][2]));
                        $default_price.html(price_to_str(variant_ids[k][3]));
                    });
                    if (variant_ids[k][3]-variant_ids[k][2]>0.01) {
                        $default_price.closest('.oe_website_sale').addClass("discount");
                        $optional_price.closest('.oe_optional').show().css('text-decoration', 'line-through');
                    } else {
                        $optional_price.closest('.oe_optional').hide();
                    }
                    product_id = variant_ids[k][0];
                    prod_qty = variant_ids[k][4];
                    update_product_image(this, product_id);
                    break;
                }
            }

            $parent.find("input.js_variant_change:radio, select.js_variant_change").each(function () {
                var $input = $(this);
                var id = +$input.val();
                var values = [id];

                $parent.find("ul:not(:has(input.js_variant_change[value='" + id + "'])) input.js_variant_change:checked, select.js_variant_change").each(function () {
                    values.push(+$(this).val());
                });

                for (var k in variant_ids) {
                    if (!_.difference(values, variant_ids[k][1]).length) {
                        return;
                    }
                }
                $input.closest("label").addClass("css_not_available");
                $input.find("option[value='" + id + "']").addClass("css_not_available");
            });

            if (product_id) {
                $parent.removeClass("css_not_available");
                $product_id.val(product_id);
                $parent.find("#add_to_cart").removeClass("disabled");
                if ($('#rent_days').data('dateRangePicker')){
    		    	$('#rent_days').data('dateRangePicker').destroy();
    	    	}
            	$('#rent_days').val('');
            } else {
                $parent.addClass("css_not_available");
                $product_id.val(0);
                $parent.find("#add_to_cart").addClass("disabled");
            }
            if (prod_qty == 0){
            	$('.outstock').removeClass('hidden');
            	$('.rent_buy > .btn.btn-primary.active').addClass('disabled');
            	$('.rent_buy > .btn.btn-primary.js_check_product.buy-submit').addClass('disabled');
            	$('#rent_days').prop('disabled', true);
            	$('.p_ad2cart').addClass('hidden');
            	$('.d_ad2cart').removeClass('hidden');
            }
            if (prod_qty > 0){
            	$('.outstock').addClass('hidden');
            	$('.rent_buy > .btn.btn-primary.active').removeClass('disabled');
            	$('.rent_buy > .btn.btn-primary.js_check_product.buy-submit').removeClass('disabled');
            	$('#rent_days').prop('disabled', false);
            	$('.p_ad2cart').removeClass('hidden');
            	$('.d_ad2cart').addClass('hidden');
            }
        });

        $('div.js_product', oe_website_sale).each(function () {
            $('input.js_product_change', this).first().trigger('change');
        });

        $('.js_add_cart_variants', oe_website_sale).each(function () {
            $('input.js_variant_change, select.js_variant_change', this).first().trigger('change');
        });

        $('.oe_cart').on('click', '.js_change_shipping', function() {
          if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_shipping').find('.panel.border_primary');
            $old.find('.btn-ship').toggle();
            $old.addClass('js_change_shipping');
            $old.removeClass('border_primary');

            var $new = $(this).parent('div.one_kanban').find('.panel');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_shipping');
            $new.addClass('border_primary');

            var $form = $(this).parent('div.one_kanban').find('form.hide');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
          }
        });
        $('.oe_cart').on('click', '.js_edit_address', function() {
            $(this).parent('div.one_kanban').find('form.hide').attr('action', '/shop/address').submit();
        });
        $('.oe_cart').on('click', '.js_delete_product', function(e) {
            e.preventDefault();
            $(this).closest('tr').find('.js_quantity').val(0).trigger('change');
        });

        if ($('.oe_website_sale .dropdown_sorty_by').length) {
            // this method allow to keep current get param from the action, with new search query
            $('.oe_website_sale .o_website_sale_search').on('submit', function (event) {
                var $this = $(this);
                if (!event.isDefaultPrevented() && !$this.is(".disabled")) {
                    event.preventDefault();
                    var oldurl = $this.attr('action');
                    oldurl += (oldurl.indexOf("?")===-1) ? "?" : "";
                    var search = $this.find('input.search-query');
                    window.location = oldurl + '&' + search.attr('name') + '=' + encodeURIComponent(search.val());
                }
            });
        }

        if ($(".checkout_autoformat").length) {
            $(oe_website_sale).on('change', "select[name='country_id']", function () {
                clickwatch(function() {
                    if ($("#country_id").val()) {
                        ajax.jsonRpc("/shop/country_infos/" + $("#country_id").val(), 'call', {mode: 'shipping'}).then(
                            function(data) {
                                // placeholder phone_code
                                //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

                                // populate states and display
                                var selectStates = $("select[name='state_id']:visible");
                                // dont reload state at first loading (done in qweb)
                                if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                                    if (data.states.length) {
                                        selectStates.html('');
                                        _.each(data.states, function(x) {
                                            var opt = $('<option>').text(x[1])
                                                .attr('value', x[0])
                                                .attr('data-code', x[2]);
                                            selectStates.append(opt);
                                        });
                                        selectStates.parent('div').show();
                                    }
                                    else {
                                        selectStates.val('').parent('div').hide();
                                    }
                                    selectStates.data('init', 0);
                                }
                                else {
                                    selectStates.data('init', 0);
                                }

                                // manage fields order / visibility
                                if (data.fields) {
                                    if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                                        $(".div_zip").before($(".div_city"));
                                    }
                                    else {
                                        $(".div_zip").after($(".div_city"));
                                    }
                                    var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                                    _.each(all_fields, function(field) {
                                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                                    });
                                }
                            }
                        );
                    }
                }, 500);
            });
        }
        $("select[name='country_id']").change();
    });

    $('.ecom-zoomable img[data-zoom]').zoomOdoo({ attach: '#o-carousel-product'});
    
    function cal_init() {
    	var sel_prod_id = $('.product_id').val();
		ajax.jsonRpc("/booked", 'call', {'prod_id':sel_prod_id
	    }).then(function(res) {
	    	var data = res;
	    	var today = new Date(); 
			var dd = today.getDate(); 
			var mm = today.getMonth()+1; //January is 0! 
			var yyyy = today.getFullYear(); 
			if(dd<10){ dd='0'+dd } 
			if(mm<10){ mm='0'+mm } 
			var today = dd+'/'+mm+'/'+yyyy;
			var future_booked = yyyy+'-'+mm+'-'+dd;
			
	    	var booked_days = [];
	    	if ($('#rent_days').data('dateRangePicker')){
		    	$('#rent_days').data('dateRangePicker').destroy();
	    	}
	    	$('#rent_days').val('');
	    	$('#rent_days').dateRangePicker({
                singleMonth: true,
                startOfWeek: 'monday',
				startDate: today,
                minDays: 0,
                maxDays: 0,
                beforeShowDay: function (date) {
                    var array_booked = [];
                    var array_buffer = [];
                    booked_days = [];
                    _.each(data, function (item) {
                            if (item.state == "booked") {
                            	var dd = item.booked_date.split(',');
                            	_.each(dd, function(d){
                            		if (Date.parse(d) >= Date.parse(future_booked)){
                            			booked_days.push(d);
                            		}
                            	});
                                if (array_booked) {
                                    array_booked = array_booked + ',' + (item.booked_date.split(','));
                                    array_buffer = array_buffer + ',' + (item.buffer_days.split(','));
                                } else {
                                    array_booked = item.booked_date.split(',');
                                    array_buffer = item.buffer_days.split(',');
                                }
                            }
                    });

                    var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
                    if (array_booked.indexOf(string) != -1) {
                        return [false, "booked", "booked"];
                    } else if (array_buffer.indexOf(string) != -1) {
                    	return [false, "laundry", "laundry"];
                    } else {
                        return [true, "", ""];
                    }

                },
                format: 'DD/MM/YYYY',
            }).bind('datepicker-closed',function() {
            	var price = eval($('div.js_product').find('span[itemprop="rent_price"]')[0].innerHTML);
	            var rent_days = $('#rent_days').val();
	            if (rent_days) {
	            	var bkdays = rent_days.split('  ')[0].split('to');
	            	var from = bkdays[0].split("/");
	            	var f = new Date(from[2], from[1] - 1, from[0]);
	            	var to = bkdays[1].split("/");
	            	var t = new Date(to[2], to[1] - 1, to[0]);
	            	var days = Math.round((t-f)/(1000*60*60*24)) + 1;

	            	var rent_price = _calculate_rent_price(days, price);
	                $('div.js_product').find('#rentp span.oe_currency_value')[0].innerHTML = rent_price.toString();
	                $("#rental_price")[0].value = rent_price;
	                $('div.js_product').find("#rent_days").val($("#rent_days").val() + '  ( ' + days.toString() + ' days)');
	                $('#days').val(days.toString());
	                $('#add_to_cart').removeClass('disabled');
	                $('#warn_msg').css('display','none');
	            }
            });
	    	
    		$('#rent_days').data('dateRangePicker').open();
    		
	        // calculate price
	        var _calculate_rent_price = function(days, price) {
	            var total_price = 0;
	            if (days) {
	                // count for weeks and price
	                var weeks = parseInt(days / 7);
	                days = days % 7;
	                if (days > 3) {
	                    weeks += 1;
	                    days = 0;
	                }
	                total_price = price * weeks * 1.5;
	
	                // count for 3-days
	                var tdays = parseInt(days / 3);
	                days = days % 3;
	                total_price += price * tdays;
	
	                // count for 2 day (actually for a day)
	                if (days > 1) {
	                    days = 0;
	                    total_price += price * 0.75;
	                }
	
	                // count for a day (actually for 7 hour)
	                if (days) {
	                    total_price += price * 0.50;
	                }
	            }
	            return parseFloat(parseFloat(total_price).toFixed(2));
	        };
	        
	    });
    }
    
    
    $('document').ready(function(){
    	$('#add_to_cart').addClass('disabled');
	    $('#rent_days').on('click', function () {
	    	$('#add_to_cart').addClass('disabled');
    		cal_init();
	    });

	    // Add a product into the cart
        $(".oe_website_sale form[action='/shop/cart/update'] label.buy-submit").off('click').on('click', function(evt) {
        	if (!evt.isDefaultPrevented() && !$(this).is(".disabled")) {
        		var sel_prod_id = $('.product_id').val();
        		ajax.jsonRpc("/booked", 'call', {'prod_id':sel_prod_id
        	    }).then(function(res) {
        	    	var data = res;
        	    	var booked_days = [];
        	    	var today = new Date(); 
        			var dd = today.getDate(); 
        			var mm = today.getMonth()+1; //January is 0! 
        			var yyyy = today.getFullYear(); 
        			if(dd<10){ dd='0'+dd } 
        			if(mm<10){ mm='0'+mm } 
        			var future_booked = yyyy+'-'+mm+'-'+dd;
                    _.each(data, function (item) {
                            if (item.state == "booked") {
                            	var dd = item.booked_date.split(',');
                            	_.each(dd, function(d){
                            		if (Date.parse(d) >= Date.parse(future_booked)){
                            			booked_days.push(d);
                            		}
                            	});
                            }
                    });
                    if (booked_days.length > 0){
	            		$("#quickwarningModal").dialog({
							modal: true,
							autoOpen: false,
							title: _t("IMPORTANT!"),
							minHeight: 170,
							maxHeight: 170,
							height: 170,
							width: 400,
							open: function() {
								$('.ui-widget-overlay').bind('click', function() {
									$('#quickwarningModal').dialog('close');
								})
							}
						});
						$("#quickwarningModal").dialog('open');
	            	} else {
	            		$(".oe_website_sale form[action='/shop/cart/update'] label.buy-submit").closest('form').submit();
	            	}
        	    });
            }
        });
        $('.oe_website_sale #add_to_cart').on('click', function (event) {
        	if(!$('#rent_days').val()) {
        		$('#warn_msg').css('display','block');
        		$('#rent_days').focus();
        	}
        	if ($('#rent_days').val()) {
        		$('#warn_msg').css('display','none');
	            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
	                $(this).closest('form').submit();
	            }
	            if ($(this).hasClass('a-submit-disable')){
	                $(this).addClass("disabled");
	            }
	            if ($(this).hasClass('a-submit-loading')){
	                var loading = '<span class="fa fa-cog fa-spin"/>';
	                var fa_span = $(this).find('span[class*="fa"]');
	                if (fa_span.length){
	                    fa_span.replaceWith(loading);
	                }
	                else{
	                    $(this).append(loading);
	                }
	            }
        	}
        });
        
    });
});
