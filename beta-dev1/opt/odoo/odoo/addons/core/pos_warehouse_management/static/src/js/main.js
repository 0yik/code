odoo.define('pos_warehouse_management.pos_warehouse_management', function (require) {
"use strict";
 	var Model = require('web.DataModel');
	var gui = require('point_of_sale.gui');
	var pos_model = require('point_of_sale.models');
	var SuperOrderline =  pos_model.Orderline.prototype;
	var core = require('web.core');
	var _t = core._t;
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var OutOfStockPopup = require('pos_stock.pos_stock');
	
	OutOfStockPopup.include({
		events : {
			'click .button.show_other_stocks': 'show_other_stock_locations',
			'click .button.cancel': 'click_cancel',
		},

		show_other_stock_locations: function() {
			var self =this;
			if (self.pos.config.related_stock_location_ids.length){
				(new Model('product.product')).call('get_product_stock_info',[{
					'location_ids' : self.pos.config.related_stock_location_ids,
					'pricelist_id': self.pos.pricelist.id,
					'product_id': self.options.product_id,
					'stock_type': self.pos.config.wk_stock_type,
				}])
				.then(function(result) {
					if (result) {
						self.pos.gui.show_popup('product_stock',{
						'stock_info'  : result,
						'product_info': [self.options.product_id,self.pos.db.product_by_id[self.options.product_id].display_name]
						});
					}
					else{
						self.$('.body').html("Product is not available in other related stock locations")
						self.$('.button.show_other_stocks').css('display','none');
				}
				}).fail(function(unused, event) {
					self.gui.show_popup('error', {
						title: _t('Failed To Load Stock Locations.'),
						body: _t('Please make sure you are connected to the network.'),
					});
					event.preventDefault();
				});
			}
		},
		
		show: function(options){
			var self = this;
			this.options = options || ''; 
			self._super(options);
		}
	});

	pos_model.Orderline = pos_model.Orderline.extend({
		export_as_JSON: function() {
			var self = this;
			var loaded=SuperOrderline.export_as_JSON.call(this);
			loaded.stock_location_id=self.stock_location_id;
			return loaded;
		},
	});

	var ProductStockPopup = PopupWidget.extend({
		template:'ProductStockPopup',
		events:{
			'click .button.cancel': 'click_cancel',
			'click .stock_line' : 'click_stock_location_line',
			'click .button.apply'  :'wk_add_product_to_orderline'
		},
		
		click_stock_location_line: function(event){
			var self = this;
			var id = $(event.target).parent().data('line-id')
			this.stock_line_select(event,$(event.target),id);
		},

		stock_line_select: function(event,$line,id){

			if ($line.parent().hasClass('selected')){
				$line.parent().removeClass('selected');
				event.target.parentNode.style.backgroundColor = '';
				this.$('.product_qty').css('display','none');
			}
			else{
				this.$('.stock_line.selected').css('background-color','');
				this.$('.stock_line.selected').removeClass('selected');
				$line.parent().addClass('selected');
				event.target.parentNode.style.backgroundColor = '#6EC89B'
				this.$('.product_qty').css('display','block');
				this.$('#qty_input').focus()
			}
    	},

		wk_add_product_to_orderline: function() {
			var self = this;
			var availabe_qty = parseInt(this.$('.stock_line.selected').find('.available_qty').text())
			var entered_qty = parseFloat(this.$('.product_qty').find('#qty_input').val())
			var order = self.pos.get_order();
			var location_id = this.$('.stock_line.selected').data('line-id')
			var product = self.pos.db.product_by_id[self.options.product_info[0]]
				
			if(availabe_qty >= entered_qty && entered_qty > 0){
				$('.orderline.selected').removeClass('selected');
				var orderline = new pos_model.Orderline({}, {
					pos: self.pos,
					order: order,
					product: product,
					stock_location_id:location_id,
					availabe_qty: availabe_qty,
				});
				orderline.product = product;
				orderline.set_unit_price(product.list_price);
				orderline.stock_location_id = location_id;
				orderline.set_quantity(entered_qty);
				orderline.comment = 1.0;
				order.add_orderline(orderline);
				self.pos.gui.close_popup();
			}
			else
			{
				$("#qty_input").css("background-color","burlywood");
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},100);
				setTimeout(function(){
					$("#qty_input").css("background-color","burlywood");
				},200);
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},300);
				setTimeout(function(){
					$("#qty_input").css("background-color","burlywood");
				},400);
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},500);
				this.$('#qty_input').focus()
				return;
			}
		},
	});
	gui.define_popup({name:'product_stock',widget:ProductStockPopup});
});