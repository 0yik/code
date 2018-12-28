odoo.define('payment_method_discount.payment_method_discount', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var models = require('point_of_sale.models');
var gui = require('point_of_sale.gui');
var _t  = require('web.core')._t;

var _super_posmodel = models.PosModel.prototype;
var apply_discount = false;
var discount_paymentline = false

models.load_fields('account.journal',['discount_type','discount_value']);
models.load_fields('product.product','is_discount_product');

screens.PaymentScreenWidget.include({

    click_back: function(){
        var order = this.pos.get_order();
        var orderlines = order.orderlines.models;
        for(var i = 0, len = orderlines.length; i < len; i++){
            if(orderlines[i].product.is_discount_product == true){
                order.remove_orderline(orderlines[i].id);
                apply_discount = false;
                discount_paymentline = false;
            }
        }
        this.gui.show_screen('products');
    },

    click_paymentmethods: function(id) {
        var cashregister = null;
        var order = this.pos.get_order();
        var total = order ? order.get_total_with_tax() : 0;

        var orderlines = order.orderlines.models;
        for(var i = 0, len = orderlines.length; i < len; i++){
            if(orderlines[i].product.is_discount_product == true){
                  apply_discount = true;
            }
        }

        var product;
        var products = this.pos.db.product_by_id;
        var product = _.filter(products, function(product){
            return product.is_discount_product;
        });

        product = this.pos.db.get_product_by_id(product[0].id)
        for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
            if ( this.pos.cashregisters[i].journal_id[0] === id ){
                cashregister = this.pos.cashregisters[i];
                if (apply_discount == false){
                    if (typeof product !== "undefined") {
                        //calculate discount price based on selected payment method.
                        if(cashregister.journal['discount_type'] == "Amount"){
                            var discount_price = cashregister.journal['discount_value']
                            order.add_product(product, {price: -discount_price, quantity:1,});
                            apply_discount = true;
                            break;
                        }
                        if(cashregister.journal['discount_type'] == "Percentage"){
                            var discount_price = (total * cashregister.journal['discount_value']) / 100;
                            order.add_product(product, {price: -discount_price, quantity:1,});
                            apply_discount = true;
                            break;
                        }
                    }
                }
            }
        }

        this.pos.get_order().add_paymentline( cashregister );
        if(discount_paymentline == false && apply_discount == true){
            discount_paymentline = this.pos.get_order().selected_paymentline.cid
        }

        this.reset_input();
        this.render_paymentlines();
    },

    click_delete_paymentline: function(cid){
        var lines = this.pos.get_order().get_paymentlines();
        var order = this.pos.get_order()

        for ( var i = 0; i < lines.length; i++ ) {
            if (lines[i].cid === cid) {
                this.pos.get_order().remove_paymentline(lines[i]);

                if (cid === discount_paymentline){
                    var orderlines = order.orderlines.models;
                    for(var i = 0, len = orderlines.length; i < len; i++){
                        if(orderlines[i].product.is_discount_product == true){
                            order.remove_orderline(orderlines[i].id);
                            apply_discount = false;;
                            discount_paymentline = false;
                            break;
                        }
                    }
                }
                this.reset_input();
                this.render_paymentlines();
            }
        }
    },


    });
});

