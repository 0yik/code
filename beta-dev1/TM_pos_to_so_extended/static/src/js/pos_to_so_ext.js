odoo.define('TM_pos_to_so_extended.TM_pos_to_so_extended', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var ActionManager1 = require('web.ActionManager');
    var PopupWidget = require("point_of_sale.popups");
    var CreateSalesOrder = require("pos_to_sales_order.pos_to_sales_order")
    var gui = require('point_of_sale.gui');
    var QWeb = core.qweb;
    var _t = core._t;

    var promo_popupso = null;
    for (var index=1; index <= gui.Gui.prototype.popup_classes.length; index++) { 
    	if(gui.Gui.prototype.popup_classes[index] && gui.Gui.prototype.popup_classes[index].name=='Create_Sales_Order_popup_widget'){ 
    		promo_popupso = gui.Gui.prototype.popup_classes[index].widget 
    		gui.Gui.prototype.popup_classes.splice(index, 1); 
    	} 
    }

    var CreateSalesOrderPopupWidget = promo_popupso.extend({ 
    	template: 'CreateSalesOrderPopupWidget',
    	events: _.extend({}, PopupWidget.prototype.events, {
    	    'click .apply_promotion': 'get_promotion_programs',
    	    'click .diffrent_address': 'customer_diffrent_address',
    	    'click .extra_fee': 'delivery_extra_fees',
    	    'click .wk_create_order': 'create_delivery_sale_order',
    	}),
    	get_promotion_programs: function(){
    		var self = this;
    		var contents = $('#promotions_list_so');
    		contents.html($(QWeb.render('list_of_promo',{widget: this, promotions:this.pos.promotions})));
    		$('.promotion-line').click(function () {
    			$('.remove_promotion').prop('disabled',false);
    			var promotion_id = parseInt($(this).data()['id']);
    			var promotion = self.pos.promotion_by_id[promotion_id];
    			var type = promotion.type;
    			var order = self.pos.get('selectedOrder');
    			if (order.orderlines.length) {
    			    if (type == '1_discount_total_order') {
    			        order.compute_discount_total_order(promotion);
    			        // self.gui.close_popup();
    			    }
    			    if (type == '2_discount_category') {
    			        order.compute_discount_category(promotion);
    			        // self.gui.close_popup();
    			    }
    			    if (type == '3_discount_by_quantity_of_product') {
    			        order.compute_discount_by_quantity_of_products(promotion);
    			        // self.gui.close_popup();
    			    }
    			    if (type == '4_pack_discount') {
    			        order.compute_pack_discount(promotion);
    			        // self.gui.close_popup();
    			    }
    			    if (type == '5_pack_free_gift') {
    			        order.compute_pack_free_gift(promotion);
    			        // self.gui.close_popup();
    			    }
    			    if (type == '6_price_filter_quantity') {
    			        order.compute_price_filter_quantity(promotion);
    			        // self.gui.close_popup();
    			    }
    		    	if (type == '7_discount_amount_with_sales') {
    		    		order.compute_discount_total_minimum_sales(promotion);
    		    		// self.gui.close_popup();
    		    	}
    		    	if (type == '9_second_item_disc_with_min_max_qty') {
    		    		order.compute_sec_discount_minimax_sales(promotion);
    		    		// self.gui.close_popup();
    		    	}
    			}
    		});
    		$('.remove_promotion').click(function () {
    		    var order = self.pos.get('selectedOrder');
    		    var lines = order.orderlines.models;
    		    var lines_remove = [];
    		    $('.remove_promotion').prop('disabled','disabled');
    		    var i = 0;
    		    while (i < lines.length) {
    		        var line = lines[i];
    		        if (line.promotion && line.promotion == true) {
    		            lines_remove.push(line)
    		        }
    		        i++;
    		    }
    		    order.remove_promotion_lines(lines_remove)
    		    order.trigger('change', order);
    		    $('#promotions_list_so').html('');
    		    $('.apply_promotion').prop( "checked", false );
    		});

    	},

    	customer_diffrent_address: function() {
    	    if ($('.diffrent_address').is(':checked')) {
    	        $('.wk_address').show();
    	    } else {
    	        $('.wk_address').hide();
    	    }
    	},
    	delivery_extra_fees: function() {
    	    var self = this;
    	    if ($('.extra_fee').is(':checked')) {
    	        if (self.pos.config.extra_price_product_id[0] != undefined)
    	            $('.extra_fee_value').show();
    	        else {
    	            $('.extra_fee_value').hide();
    	            $(".extra_fee").prop('checked', false);
    	            alert("Extra price product is not selected");
    	        }
    	    } else
    	        $('.extra_fee_value').hide();
    	},
    	create_delivery_sale_order: function() {
    	    var self = this;
    	    var order = self.pos.get('selectedOrder');
    	    var note = $('.wk_note').val();
    	    var exp_date = $('.input_date').val();
    	    var client_fields = false;
    	    var client = order.get_client();
    	    var user = self.pos.cashier || self.pos.user;
    	    if ($('.extra_fee').is(':checked')) {
    	        var product = self.pos.db.get_product_by_id(self.pos.config.extra_price_product_id[0]);
    	        if ($.isNumeric($('.extra_fee_value').val())) {
    	            var extra_amout = parseInt($('.extra_fee_value').val());
    	            order.add_product(product, {
    	                price: extra_amout
    	            });
    	        }
    	    }
    	    var orderdata = order.export_as_JSON();
    	    var orderLine = order.orderlines;
    	    if ($('.diffrent_address').is(':checked')) {
    	        client_fields = self.return_client_details(client.id);
    	        if (client_fields != false) {
    	            self.create_sale_order_rpc([orderdata, note, user.id, client_fields, exp_date]);
    	        } else {
    	            self.pos.gui.show_popup('pos_to_sale_order_custom_message', {
    	                'title': _t("Error"),
    	                'body': _t("Customer name is required."),
    	            });
    	        }
    	    } else {
    	        self.create_sale_order_rpc([orderdata, note, user.id, client_fields, exp_date]);
    	    }
    	},
    	create_sale_order_rpc: function(values) {
    	    var self = this;
    	    (new Model('pos.sales.order')).call('create_pos_sale_order', values)
    	    .fail(function(unused, event) {
    	        self.gui.show_popup('error', {
    	            'title': _t("Error!!!"),
    	            'body': _t("Check your internet connection and try again."),
    	        });
    	    })
    	    .done(function(result) {
    	        self.pos.delete_current_order();
    	        self.gui.show_popup('orderPrintPopupWidget', {
    	            'title': result.name,
    	            'order_id': result.id
    	        });
    	    });
    	},
    	return_client_details: function(partner_id) {
    	    var self = this;
    	    var fields = {};
    	    this.$('.wk_address').each(function(idx, el) {
    	        fields[el.name] = el.value;
    	    });
    	    if (!fields.name) {
    	        return false;
    	    }
    	    fields.id = partner_id || false;
    	    fields.country_id = fields.country_id || false;
    	    return fields;
    	},
    	renderElement: function() {
    	    var self = this;
    	    this._super();
    	    this.$('.wk_address').hide();
    	    this.$('.extra_fee_value').hide();
    	},
    });

    gui.define_popup({ name: 'Create_Sales_Order_popup_widget', widget: CreateSalesOrderPopupWidget });
    return CreateSalesOrderPopupWidget;


});