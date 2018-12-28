odoo.define('wv_pos_customer_display', function(require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var _t = core._t;


    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        customer_display: function(type, data){
            var self = this;
            if (this.config.allow_customer_display != true)
                return;
            var currency_rounding = Math.ceil(Math.log(1.0 / this.currency.rounding) / Math.log(10));

            if (type == 'add_update_line'){
                var line = data['line'];
                var price_unit = line.get_unit_price();
                var discount = line.get_discount();
                if (discount) {
                    price_unit = price_unit * (1.0 - (discount / 100.0));
                    }
                price_unit = price_unit.toFixed(currency_rounding);
                var qty = line.get_quantity();
                if (qty.toFixed(0) == qty) {
                    qty = qty.toFixed(0);
                }
                var unit = line.get_unit();
                var unit_display = '';
                if (unit && !unit.is_unit) {
                    unit_display = unit.name;
                }
                var l21 = qty + unit_display + ' x ' + price_unit;
                var l22 = ' ' + line.get_display_price().toFixed(currency_rounding);
                var lines_to_send = new Array(line.get_product().display_name,l21);

            } else if (type == 'removeOrderline') {
                var line = data['line'];
                var lines_to_send = new Array(_t("Delete Item"), line.get_product().display_name);

            } else if (type == 'addPaymentline') {
                var total = this.get('selectedOrder').get_total_with_tax().toFixed(currency_rounding);
                var lines_to_send = new Array(_t("TOTAL: "), total);

            } else if (type == 'removePaymentline') {
                var line = data['line'];
                var amount = line.get_amount().toFixed(currency_rounding);
                var lines_to_send = new Array(_t("Cancel Payment"), line.cashregister.journal_id[1]);

            } else if (type == 'update_payment') {
                var change = data['change'];
                var lines_to_send = new Array(_t("Your Change:"),change);

            } else if (type == 'newOrder') {
                var lines_to_send = new Array(this.config.customer_display_next_l1,this.config.customer_display_next_l2);

            } else if (type == 'closePOS') {
                var lines_to_send = new Array(this.config.customer_display_closed_l1,this.config.customer_display_closed_l2);
            } else {
                console.warn('Unknown message type');
                return;
            }
            function ledDisplay(line1,line2){  
                try{  
                    var xmlhttp;
                    if (window.XMLHttpRequest)  
                      { 
                      xmlhttp=new XMLHttpRequest();  
                      }  
                    else  
                      {
                      xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");  
                      }  
                      xmlhttp.open("GET",self.config.customer_display_ip+"/"+String(line1)+"___"+String(line2),false);  
                      xmlhttp.send();  
                    }catch(err){
                }  
            } 

            ledDisplay(lines_to_send[0],lines_to_send[1]);            
        },

        push_order: function(order){
            var res = PosModelSuper.prototype.push_order.call(this, order);
            if (order) {
                this.customer_display('newOrder', {'order' : order});
            }
            return res;
        },

    });



    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity){
            var res = OrderlineSuper.prototype.set_quantity.call(this, quantity);
            if (quantity != 'remove') {
                var line = this;
                if(this.selected){
                    this.pos.customer_display('add_update_line', {'line': line});
                }
            }
            return res;
        },

        set_discount: function(discount){
            var res = OrderlineSuper.prototype.set_discount.call(this, discount);
            if (discount) {
                var line = this;
                if(this.selected){
                    this.pos.customer_display('add_update_line', {'line': line});
                }
            }
            return res;
        },

        set_unit_price: function(price){
            var res = OrderlineSuper.prototype.set_unit_price.call(this, price);
            var line = this;
            if(this.selected){
                this.pos.customer_display('add_update_line', {'line': line});
            }
            return res;
        },

    });

    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            var res = OrderSuper.prototype.add_product.call(this, product, options);
            if (product) {
                var line = this.get_last_orderline();
                this.pos.customer_display('add_update_line', {'line' : line});
            }
            return res;
        },

        remove_orderline: function(line){
            if (line) {
                this.pos.customer_display('removeOrderline', {'line' : line});
            }
            return OrderSuper.prototype.remove_orderline.call(this, line);
        },

        remove_paymentline: function(line){
            if (line) {
                this.pos.customer_display('removePaymentline', {'line' : line});
            }
            return OrderSuper.prototype.remove_paymentline.call(this, line);
        },

        add_paymentline: function(cashregister){
            var res = OrderSuper.prototype.add_paymentline.call(this, cashregister);
            if (cashregister) {
                this.pos.customer_display('addPaymentline', {'cashregister' : cashregister});
            }
            return res;
        },

    });

    screens.PaymentScreenWidget.include({
        render_paymentlines: function(){
            var res = this._super();
            var currentOrder = this.pos.get_order();
            if (currentOrder) {
                var paidTotal = currentOrder.get_total_paid();
                var dueTotal = currentOrder.get_total_with_tax();
                var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
                if (change) {
                    var change_rounded = change.toFixed(2);
                    this.pos.customer_display('update_payment', {'change': change_rounded});
                }
            }
            return res;
        },
    });

    gui.Gui.include({
        close: function(){
            this._super();
            this.pos.customer_display('closePOS', {});
        },
    });

    chrome.ProxyStatusWidget.include({
        start: function(){
            this._super();
            this.pos.customer_display('newOrder', {});
        },
    });

    screens.PaymentScreenWidget.include({
        show: function(){
            this._super();
            this.pos.customer_display('addPaymentline', {});
        },
    });
});
