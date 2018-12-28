odoo.define('pos_transfer_product.floors', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var SuperPosModel = models.PosModel.prototype;
    var _t = core._t;

    screens.ProductScreenWidget.include({
        renderElement: function(){
            var self = this;
            this._super();
            this.$('.transfer-item-button').click(function(){
                self.pos.transfer_orderline_to_different_table();
            });
        },
    });

    models.PosModel = models.PosModel.extend({
        transfer_orderline_to_different_table: function () {
            this.orderline_to_transfer_to_different_table = this.get_order().get_selected_orderline();
            this.set_table(null);
        },
        // set_order: function(order){
		// 	SuperPosModel.set_order.call(this,order);
		// 	if(order != null && !order.is_return_order){
		// 		if (this.orderline_to_transfer_to_different_table) {
         //            order.add_orderline(this.orderline_to_transfer_to_different_table);
         //            this.orderline_to_transfer_to_different_table = null;
         //        }
		// 		$("#cancel_refund_order").hide();
		// 	}
		// 	else{
		// 		$("#cancel_refund_order").show();
		// 	}
		// },
        set_table: function(table) {
            var res = SuperPosModel.set_table.apply(this, arguments);
            var order = this.get_order();
            if( order ){
                if (this.orderline_to_transfer_to_different_table) {
                    order.add_orderline(this.orderline_to_transfer_to_different_table);
                    this.orderline_to_transfer_to_different_table = null;
                }
            }
            return res;
        }
    });

});