odoo.define('pos_promotion_program.pos_promotion_program', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var Model = require('web.DataModel');
	var _t = core._t;

	models.load_models([
		{
			model: 'import.pos.promotion.product',
			fields: [],
			loaded: function (self, exceptionProduct) {
				self.exceptionProduct = exceptionProduct;
				self.exceptionProduct_by_id = {};
				self.exceptionProd_by_id = {};
				self.exceptionProduct_ids = []
				var i = 0;
				while (i < exceptionProduct.length) {
					self.exceptionProduct_by_id[exceptionProduct[i].id] = exceptionProduct[i];
					self.exceptionProduct_ids.push(exceptionProduct[i].id);

					if (!self.exceptionProd_by_id[exceptionProduct[i].line_id[0]]) {
					    self.exceptionProd_by_id[exceptionProduct[i].line_id[0]] = [exceptionProduct[i]]
					} else {
					    self.exceptionProd_by_id[exceptionProduct[i].line_id[0]].push(exceptionProduct[i])
					}
					i++;
				}
			}
		},{
			model: 'minimum.sales.discount',
			fields: [],
			loaded: function (self, minsales) {
				self.minsales = minsales;
				self.minsales_by_id = {};
				self.minsales_ids = []
				var i = 0;
				while (i < minsales.length) {
					// self.minsales_by_id[minsales[i].line_id[0]] = minsales[i];
					self.minsales_ids.push(minsales[i].id);
					if (!self.minsales_by_id[minsales[i].line_id[0]]) {
					    self.minsales_by_id[minsales[i].line_id[0]] = [minsales[i]]
					} else {
					    self.minsales_by_id[minsales[i].line_id[0]].push(minsales[i])
					}
					i++;
				}
			}
		},{
			model:"minimum.maximum.sales.discount",
			fields:[],
			loaded: function(self, minmax_sec) {
				self.minmax_sec = minmax_sec;
				self.minmax_sec_by_id = {};
				self.minmax_sec_ids = []
				var i = 0;
				while (i < minmax_sec.length) {
					self.minmax_sec_ids.push(minmax_sec[i].id);
					if (!self.minmax_sec_by_id[minmax_sec[i].line_id[0]]) {
					    self.minmax_sec_by_id[minmax_sec[i].line_id[0]] = [minmax_sec[i]]
					} else {
					    self.minmax_sec_by_id[minmax_sec[i].line_id[0]].push(minmax_sec[i])
					}
					i++;
				}
			}
		},
	]);


	// var promo_popup = null;
	// for (var index=1; index <= gui.Gui.prototype.popup_classes.length; index++) { 
	// 	if(gui.Gui.prototype.popup_classes[index].name=='promotion_popup'){ 
	// 		promo_popup = gui.Gui.prototype.popup_classes[index].widget 
	// 		gui.Gui.prototype.popup_classes.splice(index, 1); 
	// 	} 
	// }

	// var PromoPopupWidget = promo_popup.extend({ 
	// 	template: 'promotion_popup', 
	// 	init: function (parent, options) { 
	// 		this._super(parent, options); 
	// 		this.promotions = this.pos.promotions; 
	// 	},
	// 	renderElement: function () {
	// 		var self = this;
	// 		this._super();
	// 		console.log('Call...',$('.promotion-line'));
	// 		$('.promotion-line').click(function () {
	// 			var promotion_id = parseInt($(this).data()['id']);
	// 			var promotion = self.pos.promotion_by_id[promotion_id];
	// 			var type = promotion.type;
	// 			var order = self.pos.get('selectedOrder');
	// 			if (order.orderlines.length) {
	// 				if (type == '7_discount_amount_with_sales') {
	// 					order.compute_discount_total_minimum_sales(promotion);
	// 				}
	// 			}
	// 		});
	// 	},
	// 	compute_discount_total_minimum_sales: function(promotion){
	// 		console.log('this...',promotion);
	// 	},
	// });
	
	// gui.define_popup({ name: 'promotion_popup', widget: PromoPopupWidget });

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		checking_apply_minsales_total_order_payment: function(promotion){
			var discount_lines = this.pos.minsales_by_id[promotion.id];
			var total_order = this.get_total_without_tax();
			var lines = this.orderlines.models;
			var discount_line_tmp = null;
			var discount_tmp = 0;
			var order = this.pos.get_order();
			var selected_paymentline = order.selected_paymentline
			if (discount_lines && selected_paymentline) {
			    var i = 0;
			    
			    while (i < discount_lines.length) {
			        var discount_line = discount_lines[i];
			        if (total_order >= parseInt(discount_line.minimum_sales) && discount_line.payment_method_id[0] == selected_paymentline.cashregister.journal_id[0]) {
			            discount_line_tmp = discount_line;
			            discount_tmp = parseInt(discount_line.minimum_sales)
			        }
			        i++;
			    }
			}
			return discount_line_tmp;
		},
		checking_apply_minsales_total_order: function (promotion) {
		    var discount_lines = this.pos.minsales_by_id[promotion.id];
		    var total_order = this.get_total_without_tax();
		    var lines = this.orderlines.models;
		    var discount_line_tmp = null;
		    var discount_tmp = 0;
		    if (discount_lines) {
		        var i = 0;
		        
		        while (i < discount_lines.length) {
		            var discount_line = discount_lines[i];
		            if (total_order >= parseInt(discount_line.minimum_sales)) {
		                discount_line_tmp = discount_line;
		                discount_tmp = parseInt(discount_line.minimum_sales)
		            }
		            i++;
		        }
		    }
		    return discount_line_tmp;
		},
	    compute_discount_total_minimum_sales: function(promotion){
	    	var discount_line_tmp = this.checking_apply_minsales_total_order(promotion)
	    	var total_order = this.get_total_without_tax();
	    	if (discount_line_tmp) {
	    	    var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
	    	    if (product) {
	    	        this.add_product(product, {
	    	            price: -total_order / 100 * discount_line_tmp.discount_amount
	    	        })
	    	        var selected_line = this.get_selected_orderline();
	    	        selected_line.promotion_discount_total_order = true;
	    	        selected_line.promotion = true;
	    	        selected_line.promotion_reason = 'discount ' + discount_line_tmp.discount_amount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_sales;
	    	        selected_line.trigger('change', selected_line);
	    	    
	    	    }else{
	    			this.show_popup_function();
	    		}
	    	}
	    },
	    compute_discount_total_minimum_sales_payment: function(promotion){
	    	var discount_line_tmp = this.checking_apply_minsales_total_order_payment(promotion)
	    	var total_order = this.get_total_without_tax();
	    	var product = this.pos.db.product_by_id[parseInt(promotion.product_id[0])];
	    	if (discount_line_tmp && product) {
		        this.add_product(product, {
		            price: -total_order / 100 * discount_line_tmp.discount_amount
		        })
		        var selected_line = this.get_selected_orderline();
		        selected_line.promotion_discount_total_order = true;
		        selected_line.promotion = true;
		        selected_line.promotion_reason = 'discount ' + discount_line_tmp.discount_amount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_sales;
		        selected_line.trigger('change', selected_line);

	    	}else{
	    		this.show_popup_function();
	    	}
	    },
	    checking_apply_minmaxsales: function(promotion){
	    	var product_line = {};
	    	var second_product_line = {};
	    	var first_prod_qty = 0;
	    	var i = 0;
	    	var j = 0;
	    	var sec_prod_qty = 0;

	    	var order = this.pos.get_order();
	    	var selected_orderline = this.get_selected_orderline();
	    	var orderlines = order.orderlines.models;

	    	var product_lines = this.pos.exceptionProd_by_id[promotion.id];
	    	var discount_lines = this.pos.minmax_sec_by_id[promotion.id];
	
	    	var total_order = this.get_total_without_tax();
	    	var discount_line_tmp = null;
	    	var discount_tmp = 0;

			for (var k = 0; k < product_lines.length; k++) {
				for (var j = 0; j < orderlines.length; j++) {
					if (product_lines[k].product_id[0] == selected_orderline.product.id && product_lines[k].product_id2[0] == orderlines[j].product.id){
						first_prod_qty = selected_orderline.quantity
						sec_prod_qty = orderlines[j].quantity
						product_line = product_lines[k]
					}
				}
			}
	    	if (discount_lines) {
	    	    var i = 0;
	    	    
	    	    while (i < discount_lines.length) {
	    	        var discount_line = discount_lines[i];
	    	        if (discount_line.first_min_qty <= first_prod_qty && discount_line.second_max_qty >= sec_prod_qty) {
	    	            discount_line_tmp = discount_line;
	    	            discount_tmp = parseInt(discount_line.discount_amount)
	    	        }
	    	        i++;
	    	    }
	    	}
	    	return discount_line_tmp;
	    },
	    compute_sec_discount_minimax_sales: function(promotion){
	    	var discount_line_tmp = this.checking_apply_minmaxsales(promotion);
	    	var total_order = this.get_total_without_tax();
	    	var product = this.pos.db.product_by_id[parseInt(promotion.product_id[0])];

	    	if (discount_line_tmp && product) {
		        this.add_product(product, {
		            price: -total_order / 100 * discount_line_tmp.discount_amount
		        })
		        var selected_line = this.get_selected_orderline();
		        selected_line.promotion_discount_total_order = true;
		        selected_line.promotion = true;
		        selected_line.promotion_reason = 'discount ' + discount_line_tmp.discount_amount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_sales;
		        selected_line.trigger('change', selected_line);
		        // this.gui.close_popup();
	    	}else{
	    		this.show_popup_function();
	    	}
	    },
	    show_popup_function: function(){
	    	var self = this;
	    	self.pos.gui.show_popup('error',{
	    		'title': _t('Product Service'),
	    		'body':  _t('Please select product service which is available in point of sale.'),
	    	});
	    },
	    auto_build_promotion: function () {
	        if (!this.pos.building_promotion || this.pos.building_promotion == false) {
	            if (this.pos.config.allow_promotion == true && this.pos.config.promotion_ids.length) {
	                this.pos.building_promotion = true;
	                var promotions = this.pos.promotions
	                if (promotions) {
	                    for (var i = 0; i < promotions.length; i++) {
	                        var type = promotions[i].type
	                        var order = this;
	                        if (order.orderlines.length) {
	                            if (type == '1_discount_total_order') {
	                                order.compute_discount_total_order(promotions[i]);
	                            }
	                            if (type == '2_discount_category') {
	                                order.compute_discount_category(promotions[i]);
	                            }
	                            if (type == '3_discount_by_quantity_of_product') {
	                                order.compute_discount_by_quantity_of_products(promotions[i]);
	                            }
	                            if (type == '4_pack_discount') {
	                                order.compute_pack_discount(promotions[i]);
	                            }
	                            if (type == '5_pack_free_gift') {
	                                order.compute_pack_free_gift(promotions[i]);
	                            }
	                            if (type == '6_price_filter_quantity') {
	                                order.compute_price_filter_quantity(promotions[i]);
	                            }
	                            if (type == '7_discount_amount_with_sales') {
	                            	order.compute_discount_total_minimum_sales(promotions[i]);
	                            }
	                            if (type == '8_global_disc_with_payment_type') {
	                            	order.compute_discount_total_minimum_sales_payment(promotions[i]);
	                            }
	                            if (type == '9_second_item_disc_with_min_max_qty') {
	                            	order.compute_sec_discount_minimax_sales(promotion);
	                            }
	                        }
	                    }
	                }
	                this.pos.building_promotion = false;
	            }
	        }
	    },
	});

	var promotion_button_new = screens.ActionButtonWidget.extend({
		template: 'promotion_button_new',
		button_click: function () {
			var order = this.pos.get_order();
			var OrderLines = order.orderlines;
			var promotions_show = this.pos.promotions;
			var self = this;
			var prmo_ids = [];
			var exception_promotion = [];
			var orderline_product_line = [];
			OrderLines.forEach( function(orderline){
				orderline_product_line.push(orderline.product.id)
			});
			promotions_show.forEach( function(prmo){
				
				if (prmo.item_type == 'all item no exception'){
					exception_promotion.push(prmo)
				}
				if (prmo.item_type == 'all item with exception'){
					prmo.import_line_ids.forEach( function(importLine){
						if (orderline_product_line.indexOf(self.pos.exceptionProduct_by_id[importLine].product_id[0]) >= 0 && prmo_ids.indexOf(prmo.id) < 0){
							exception_promotion.push(prmo)
							prmo_ids.push(prmo.id);
						}
					});
				}
				if (prmo.item_type == 'must include specific item'){
					OrderLines.forEach( function(orderline){
						for (var j = prmo.import_line_ids.length - 1; j >= 0; j--) {
							if (orderline.product.id == self.pos.exceptionProduct_by_id[prmo.import_line_ids[j]].product_id[0]){
								exception_promotion.push(prmo)
							}
						}
					});
				}
				if (prmo.item_type == 'specific item only'){
					OrderLines.forEach( function(orderline){
						var passt = true;
						var list_of_prod = [];
						for (var j = prmo.import_line_ids.length - 1; j >= 0; j--) {
							list_of_prod.push(self.pos.exceptionProduct_by_id[prmo.import_line_ids[j]].product_id[0])
						}
						if (list_of_prod.indexOf(orderline.product.id) >= 0) {
							var passt = true;
						}else{
							var passt = false;
						}
						if (passt == true){
							exception_promotion.push(prmo);
						}
					});
				}
			});


			var final_promotions = this.checking_buyer(exception_promotion);
			this.promotions = this.checking_proimotion(final_promotions);

			if (order && order.orderlines.length) {
				this.gui.show_popup('promotion_popup', {});
				var contents = $('#promotions_list');
				contents.append($(QWeb.render('list_of_promo',{widget: this, promotions:this.promotions})));
				$('.promotion-line').click(function () {
					var promotion_id = parseInt($(this).data()['id']);
					var promotion = self.pos.promotion_by_id[promotion_id];
					var type = promotion.type;
					var order = self.pos.get('selectedOrder');
					if (order.orderlines.length) {
					    if (type == '1_discount_total_order') {
					        order.compute_discount_total_order(promotion);
					        self.gui.close_popup();
					    }
					    if (type == '2_discount_category') {
					        order.compute_discount_category(promotion);
					        self.gui.close_popup();
					    }
					    if (type == '3_discount_by_quantity_of_product') {
					        order.compute_discount_by_quantity_of_products(promotion);
					        self.gui.close_popup();
					    }
					    if (type == '4_pack_discount') {
					        order.compute_pack_discount(promotion);
					        self.gui.close_popup();
					    }
					    if (type == '5_pack_free_gift') {
					        order.compute_pack_free_gift(promotion);
					        self.gui.close_popup();
					    }
					    if (type == '6_price_filter_quantity') {
					        order.compute_price_filter_quantity(promotion);
					        self.gui.close_popup();
					    }
				    	if (type == '7_discount_amount_with_sales') {
				    		order.compute_discount_total_minimum_sales(promotion);
				    		self.gui.close_popup();
				    	}
				    	if (type == '9_second_item_disc_with_min_max_qty') {
				    		order.compute_sec_discount_minimax_sales(promotion);
				    		self.gui.close_popup();
				    	}
					}
					
				});

				$('.remove_promotion').click(function () {
				    var order = self.pos.get('selectedOrder');
				    var lines = order.orderlines.models;
				    var lines_remove = [];
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
					self.gui.close_popup();
				});
				this.pos.auto_promotion = false;
				$('.auto-promotion').removeClass('highlight');

			}
		},
		checking_proimotion: function(promotions) {
			var self = this;
			var order = this.pos.get_order();
			var final_prom = [];
			if (promotions){
				for (var prom in promotions){
					if (promotions[prom].type != '8_global_disc_with_payment_type'){
						final_prom.push(promotions[prom]);
					}

				}
			}
			return final_prom;
		},
		checking_buyer: function(promotions) {
			var self = this;
			var order = this.pos.get_order();
			var client = this.pos.get_client();
			var final_prom = [];
			if (promotions){
				for (var prom in promotions){
					if (promotions[prom].buyer_type == 'all_buyer'){
						final_prom.push(promotions[prom]);
					}
					if (promotions[prom].buyer_type == 'member_only' && client){
						final_prom.push(promotions[prom]);
					}
					if (promotions[prom].buyer_type == 'non_member' && !client){
						final_prom.push(promotions[prom]);
					}
				}
			}
			return final_prom;
		},
	});

	screens.define_action_button({
		'name': 'promotion_button_new',
		'widget': promotion_button_new,
		'condition': function () {
			return this.pos.config.promotion_ids.length && this.pos.config.allow_promotion == true;
		},
	});

	screens.PaymentScreenWidget.include({
		show: function(){
			var self = this;
			this.pos.get_order().clean_empty_paymentlines();
			var order = this.pos.get_order();
			this.reset_input();
			this.render_paymentlines();
			this.order_changes();
			this._super();
			self.$('#promotion_pay').click(function(){
				var pass_pay = false;
				if (order.paymentlines.length == 0){
					self.gui.show_popup('error',{
						'title': _t('Select Payment'),
						'body':  _t('To apply Promotion payment amount must be Select Payment Mode'),
					});
				}else{
					if(order.get_total_with_tax() > 0){
						self.promotions = self.checking_proimotion(self.pos.promotions);					
						self.gui.show_popup('promotion_popup', {});
						var contents = $('#promotions_list');
						contents.append($(QWeb.render('list_of_promo',{widget: self, promotions:self.promotions})));
						$('.promotion-line').click(function () {
							var promotion_id = parseInt($(this).data()['id']);
							var promotion = self.pos.promotion_by_id[promotion_id];
							var type = promotion.type;
							var product = self.pos.db.product_by_id[parseInt(promotion.product_id[0])];
							if (!product){
								this.pos.gui.show_popup('error',{
									'title': _t('Configuration'),
									'body':  _t('To apply Promotion Please select Product service In Promotion.'),
								});
							}else{
								if (type == '8_global_disc_with_payment_type') {
									order.compute_discount_total_minimum_sales_payment(promotion);
								}
								self.pos.chrome.screens.payment.render_paymentlines();
								self.gui.close_popup();
							}
						});

						$('.remove_promotion').click(function () {
						    var order = self.pos.get('selectedOrder');
						    var lines = order.orderlines.models;
						    var lines_remove = [];
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
							self.gui.close_popup();
						});
					}
					else
					{
						self.gui.show_popup('error',{
							'title': _t('Zero Payment Amount'),
							'body':  _t('To apply Promotion payment amount must be greater than zero'),
						});
					}
				}

			});
		},
		checking_proimotion: function(promotions) {
			var self = this;
			var order = this.pos.get_order();
			var final_prom = [];
			if (promotions){
				for (var prom in promotions){
					if (promotions[prom].type == '8_global_disc_with_payment_type'){
						final_prom.push(promotions[prom]);
					}

				}
			}
			return final_prom;
		},
	});

});

