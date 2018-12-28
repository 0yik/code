$(document).ready(function() {
	
	/*$('#eorder').on('click', function() {
        var path = window.location.pathname.replace("/shop/cart","/shop/eorder");
        //console.log('\n location',path, window.location.pathname,  window.location);
        setTimeout(function(){
        	window.location.href = window.location.origin + path; 
        }, 3000);
    });*/
	
	$('#cust_submit').on('click', function() {
		if ($('#cust').val().length <= 0){
			alert('Please enter customer Name');
		} else {
			$('#order_customer').one('hidden.bs.modal', function() {
                $('#order_sub').modal('show'); 
            }).modal('hide');
			var path = window.location.pathname.replace("/shop/cart","/shop/eorder");
	        setTimeout(function(){
	        	window.location.href = window.location.origin + path + '?customer='+$('#cust').val(); 
	        }, 3000);
		}
	});
	
	$('.oe_cart').on('click', '.js_delete_product', function(e) {
        e.preventDefault();
        $(this).closest('tr').find('.js_quantity').val(0).trigger('change');
        $('#eorder').css('display','none');
    });
	var $primary_price = $(".oe_price:first .oe_currency_value").text().split('.')[0];
	$(".oe_price:first .oe_currency_value").text($primary_price);
	$('#tot_price').text($(".oe_price:first .oe_currency_value").text());
	
	$('.badge .oe_currency_value').each(function () {
		var $elem_val = $(this).text().split('.')[0];
		$(this).text($elem_val);
	});
	
});

odoo.define('emenu_shop.website_sale', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var ajax = require('web.ajax');
    var utils = require('web.utils');
    var core = require('web.core');
    var config = require('web.config');
    var _t = core._t;

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        function custprice_to_str(price) {
            var l10n = _t.database.parameters;
            var precision = 2;
            if ($(".decimal_precision").length) {
                precision = parseInt($(".decimal_precision").last().data('precision'));
                if (!precision) { precision = 0; } //todo: remove me in master/saas-17
            }
            var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
            formatted[0] = utils.insert_thousand_seps(formatted[0]);
            //return formatted.join(l10n.decimal_point);
            return formatted[0]
        }
        
        function update_product_image(event_source, product_id) {
            if ($('#o-carousel-product').length) {
                var $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img');
                $img.attr("src", "/web/image/product.product/" + product_id + "/image");
                $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                    .data('oe-model', 'product.product').data('oe-id', product_id);

                var $thumbnail = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img_small');
                if ($thumbnail.length !== 0) { // if only one, thumbnails are not displayed
                    $thumbnail.attr("src", "/web/image/product.product/" + product_id + "/image/90x90");
                    $('.carousel').carousel(0);
                }
            }
            else {
                var $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
                $img.attr("src", "/web/image/product.product/" + product_id + "/image");
                $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                    .data('oe-model', 'product.product').data('oe-id', product_id);
            }
            // reset zooming constructs
            $img.filter('[data-zoom-image]').attr('data-zoom-image', $img.attr('src'));
            if ($img.data('zoomOdoo') !== undefined) {
                $img.data('zoomOdoo').isReady = false;
            }
        }
        $('.oe_website_sale').off('change').on('change', function (ev) {
        	var $ul = $(ev.target).closest('.js_add_cart_variants');
            var $parent = $ul.closest('.js_product');
            var $product_id = $parent.find('.product_id').first();
            var $price = $parent.find(".oe_price:first .oe_currency_value");
            var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
            var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
            var variant_ids = $ul.data("attribute_value_ids");
            var values = [];
            var unchanged_values = $parent.find('div.oe_unchanged_value_ids').data('unchanged_value_ids') || [];

            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                values.push(+$(this).val());
            });
            values =  values.concat(unchanged_values);

            $parent.find("label").removeClass("text-muted css_not_available");
            var product_id = false;
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                	$.when(base.ready()).then(function() {
                        $price.html(custprice_to_str(variant_ids[k][2]));
                        $default_price.html(custprice_to_str(variant_ids[k][3]));
                        var $price_cal = parseFloat($price.text().replace(',','')) * parseInt($parent.find('.quantity').val());
                        $parent.find('#tot_price').text(custprice_to_str($price_cal).split('.')[0]);
                    });
                    if (variant_ids[k][3]-variant_ids[k][2]>0.01) {
                        $default_price.closest('.oe_website_sale').addClass("discount");
                        $optional_price.closest('.oe_optional').show().css('text-decoration', 'line-through');
                        $default_price.parent().removeClass('hidden');
                    } else {
                        $optional_price.closest('.oe_optional').hide();
                        $default_price.parent().addClass('hidden');
                    }
                    product_id = variant_ids[k][0];
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
            } else {
                $parent.addClass("css_not_available");
                $product_id.val(0);
                $parent.find("#add_to_cart").addClass("disabled");
            }
        });
    });
});