odoo.define('pos_print_cart_items.printcart', function (require) {
"use strict";

var core = require('web.core');
var point_of_sale = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var utils = require('web.utils');
var round_pr = utils.round_precision;

models.Orderline = models.Orderline.extend({
    get_unit_display_price: function(){
        var self = this;
        if (this.pos.config.iface_tax_included) {
            var quantity = this.quantity;
            this.quantity = 1.0;
            var price = this.get_all_prices().priceWithTax;
            this.quantity = quantity;
            return price.toFixed(2);
        } else {
            return this.get_unit_price().toFixed(2);
        }
    },
    get_display_price: function(){
        if (this.pos.config.iface_tax_included) {
            return this.get_price_with_tax().toFixed(2);
        } else {
            return this.get_base_price().toFixed(2);
        }
    },
});


models.Order = models.Order.extend({
    get_subtotal : function(){
        return round_pr(this.orderlines.reduce((function(sum, orderLine){

            var display_price= parseFloat(orderLine.get_display_price())
            var sub_total = parseFloat(sum) + display_price;

            return sub_total;
        }), 0), this.pos.currency.rounding).toFixed(2);
    },

    get_total_with_tax: function() {
        var total_with_tax = parseFloat(this.get_total_without_tax()) + parseFloat(this.get_total_tax())
        return total_with_tax.toFixed(2);
    },

    get_total_tax: function() {
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {

            var total_tax = parseFloat(sum) + parseFloat(orderLine.get_tax())
            return total_tax;
        }), 0), this.pos.currency.rounding).toFixed(2);
    },
});


models.load_fields('res.company',['fax','street','city','state_id','street2','zip']);


var QWeb = core.qweb;

point_of_sale.ActionpadWidget.include({

    renderElement: function () {
        var self = this;
        this._super()
        this.$('.set-print-cart').click(function(){

            self.gui.show_screen('PrintCart');

        });

    },

});

var PrintCartWidget = point_of_sale.ReceiptScreenWidget.extend({
    template: 'PrintCartWidget',
    show: function(){
        this._super();
        var self = this;

        this.render_change();
        this.render_receipt();
        this.handle_auto_print();
    },

    click_next: function(){
        this.gui.show_screen('products');
    },
    click_back: function(){
        this.gui.show_screen('products');
    },
    render_receipt: function(){
        this._super();
        this.$('.receipt-paymentlines').remove();
        this.$('.receipt-change').remove();
    },
    print_web: function(){
        window.print();
    },
    handle_auto_print: function() {
        if (this.should_auto_print()) {
            this.print();
            if (this.should_close_immediately()){
                this.click_next();
            }
        } else {
            this.lock_screen(false);
        }
    },
    render_receipt: function() {
        var order = this.pos.get_order();

        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!

        var yyyy = today.getFullYear();
        if(dd<10){
            dd='0'+dd;
        }
        if(mm<10){
            mm='0'+mm;
        }
        var today = dd+'/'+mm+'/'+yyyy;

        this.$('.pos-receipt-container').html(QWeb.render('PrintCartReceipt',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                customer : order.attributes,
                current_date : today,
            }));
    },
});

gui.define_screen({name:'PrintCart', widget: PrintCartWidget});

});
