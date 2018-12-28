odoo.define('pos_cross_selling.pos', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var gui = require('point_of_sale.gui');
	var PopupWidget = require('point_of_sale.popups');
	var Model = require('web.DataModel');
	var Screens = require('point_of_sale.screens');

	var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
    	add_product:function(product, options){
    		var self = this;
    		if(!self.pos.config.enable_cross_selling){
    			_super_Order.add_product.call(self, product, options);
    		}else{
    			if(options){
    				var product_list = [];
    				if(options.ac_allow == 'No'){
    					_super_Order.add_product.call(self, product, options);
    				} else {
     					(new Model('product.cross.selling')).get_func('find_cross_selling_products')(product.id).pipe(
    						function(result){
    							if(result) {
    								product_list = []
    								
    								for(var i=0;i<result.length;i++){
    									var cross_product = self.pos.db.get_product_by_id(result[i][0]);
    									cross_product.ac_subtotal = result[i][1]
    									cross_product.base_product = product.id;
    									product_list.push(cross_product);
    								}
    								self.pos.gui.show_popup('cross_selling',{'product_list':product_list});
    							} else {
        							_super_Order.add_product.call(self, product, options);
    							}
    						});
    				}
    			} else {
    				(new Model('product.cross.selling')).get_func('find_cross_selling_products')(product.id).pipe(
    					function(result){
    						if(result){
    							product_list = []
    							for(var i=0;i<result.length;i++){
    								var cross_product = self.pos.db.get_product_by_id(result[i][0]);
    								cross_product.ac_subtotal = result[i][1]
    								cross_product.base_product = product.id;
    								product_list.push(cross_product);
    							}
    							self.pos.gui.show_popup('cross_selling',{'product_list':product_list});
    						} else {
    							_super_Order.add_product.call(self, product, options);
    						}
    					});
    			}
    		}
    	},
    });

	var _super_orderline = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            json.cross_sell_id = this.get_cross_sell_id();
            json.child_line_ids = this.get_child_line_ids();
            return json;
        },
        set_cross_sell_id: function(cross_sell_id) {
	        this.set('cross_sell_id', cross_sell_id)
	    },
	    get_cross_sell_id: function() {
	        return this.get('cross_sell_id');
	    },
	    set_child_line_ids: function(ids) {
	        this.set('child_line_ids', ids)
	    },
	    get_child_line_ids: function() {
	        return this.get('child_line_ids');
	    },
	});
	
	Screens.OrderWidget.include({
        set_value: function(val) {
        	var order = this.pos.get_order();
            this.numpad_state = this.numpad_state;
            var mode = this.numpad_state.get('mode');
            var selected_orderline = order.get_selected_orderline();
            if (selected_orderline) {
            	 if( mode === 'quantity'){
            		 var line_ids = selected_orderline.get_child_line_ids();
                     if(val == 'remove' && line_ids){
                     	for(var id in line_ids){
                     		var child_line = order.get_orderline(line_ids[id]);
                     		if(child_line){
                     			child_line.set_quantity(val);
                     		}
                     	}
                     }
                     order.select_orderline(selected_orderline);
                     this._super(val);
            	 } else {
            		 this._super(val);
            	 }
            }
        },
	});

	var ProductSelectionPopupWidget = PopupWidget.extend({
	    template: 'ProductSelectionPopupWidget',
	    show: function(options){
	        options = options || {};
	        this._super(options);
	        this.product_list = options.product_list || {};
    		this.renderElement();
	    },
	    click_confirm: function(){
	    	var self = this;
	    	var fields = {}
			var currentOrder = self.pos.get_order();
			var product = this.product_list[0];
			var list_ids = [];
			$('.ac_selected_product').each(function(idx,el){
				if(el.checked){
					var qty = 1;
					var input_qty = $(".product_qty"+el.name).val();
					if(! isNaN(input_qty) && (input_qty != "") ){
						qty = parseFloat(input_qty);
					}
					if(qty > 0){
						product = self.pos.db.get_product_by_id(parseInt(el.name));
						currentOrder.add_product(product,{'ac_allow':'No',price:product.ac_subtotal,quantity:qty});
						currentOrder.get_selected_orderline().set_cross_sell_id(product.base_product);
						list_ids.push(currentOrder.get_selected_orderline().id);
					}
				}
			});
			product = self.pos.db.get_product_by_id(product.base_product);
			currentOrder.add_product(product,{'ac_allow':'No'});
			if(currentOrder.get_selected_orderline()){
				currentOrder.get_selected_orderline().set_child_line_ids(list_ids);
			}
	        this.gui.close_popup();
	    },
	    click_cancel: function(){
	    	var self = this;
	    	var product = this.product_list[0];
			var currentOrder = self.pos.get_order();
			product = self.pos.db.get_product_by_id(product.base_product);
			currentOrder.add_product(product,{'ac_allow':'No'});
			this.gui.close_popup();
	    },
	    get_product_image_url: function(product_id){
    		return window.location.origin + '/web/binary/image?model=product.product&field=image_medium&id='+product_id;
    	},
	});
	gui.define_popup({name:'cross_selling', widget: ProductSelectionPopupWidget});
});