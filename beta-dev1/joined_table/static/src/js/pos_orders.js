odoo.define('joined_table.pos_orders', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var Orderline = models.Orderline.prototype;
    var Order = models.Order.prototype;
    var OrderWidget = screens.OrderWidget.prototype;
    var round_pr = utils.round_precision;
    var SuperOrder = models.Order.prototype;
    var chrome = require('point_of_sale.chrome');
    var QWeb = core.qweb;

    models.load_fields('pos.session', ['sequence_alphabet']);

    models.Order = models.Order.extend({
        initialize: function(attributes,options){

            SuperOrder.initialize.call(this,attributes,options);
            this.order_category = this.pos.category;
            if (!options.json){
                var self = this;
                var charA = 'A';
                var charZ = 'Z';
                var alpha = [], i = charA.charCodeAt(0), j = charZ.charCodeAt(0);
                for (; i <= j; ++i) {
                    alpha.push(String.fromCharCode(i));
                }
                var order = this.pos.get('orders').models;
                var current_alpha = []
                for (var i=0; i<=order.length; i++){
                    if((order[i] && order[i].table && self.table && self.table.name == order[i].table.name) || (order[i] && this.pos.floors.length <= 0))
                    {
                    	if (self.pos.config.screen_type == "e_menu"){
                			if (order[i].emenu_order) {
                				current_alpha.push(order[i].sequence_alphabet);
        	                }
                		} else {
	                        if (order[i].order_category == order[i].pos.category) {
	                            current_alpha.push(order[i].sequence_alphabet);
	                        }
                		}
                    }
                    
                }
                if(current_alpha){
                    for(var i=0; i <= alpha.length; i++){
                        if (current_alpha.indexOf(alpha[i]) == -1){

                            this.sequence_alphabet = alpha[i] ;
                            break;
                        }
                    }
                }
            }
        },
        init_from_JSON: function(json) {
            // var client;
            Order.init_from_JSON.call(this, json);
            this.sequence_alphabet = json.sequence_alphabet;
            this.order_category = json.order_category;
        },
        export_as_JSON: function() {
            var ret= Order.export_as_JSON.call(this);
            ret.sequence_alphabet = this.sequence_alphabet;
            ret.order_category = this.order_category ? this.order_category : this.pos.category;
            return ret;
        },

        print_order_receipt: function(printer, changes) {
            var self = this;
            var sequence_alphabet = self.sequence_alphabet;
            function delay(ms) {
                var d = $.Deferred();
                setTimeout(function(){
                    d.resolve();
                }, ms);
                return d.promise();
            }
            var q = $.when();
            if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
                q = q.then(function(){
                    var receipt = QWeb.render('OrderChangeReceipt',{changes:changes, widget:this, sequence:sequence_alphabet});
                    printer.print(receipt);
                    return delay(100);
                });
            }
        }

    });
    
    // show only specific order type's order
    var PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        get_order_list: function(){
        	var category_orders = [];
        	var orders = this.get('orders').models;
        	var self = this;
        	for (var i = 0; i < orders.length; i++) {
        		if (self.config.screen_type == "e_menu"){
        			if (orders[i].emenu_order) {
	                	category_orders.push(orders[i]);
	                }
        		}
        		else {
	                if (self.category === orders[i].order_category && self.table === orders[i].table) {
	                	category_orders.push(orders[i]);
	                }
        		}
            }
        	if (self.config.screen_type == "e_menu" && category_orders.length <= 0){
        		category_orders.push(this.add_new_order());
        	}
            //return this.get('orders').models;
            return category_orders;
        },
    });
    
    //hide top buttons
    /*chrome.OrderSelectorWidget.include({
	    renderElement: function(){
            var self = this;
            this._super();
            if (self.pos.category != "dive_in"){
                $('.order-selector').hide();
            }
        },
    });*/
});
