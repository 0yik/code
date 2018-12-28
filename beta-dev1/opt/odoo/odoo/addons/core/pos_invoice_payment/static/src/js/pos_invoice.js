odoo.define('pos_invoice_payment.pos_invoice', function (require) {
"use strict";

var Class   = require('web.Class');
var Model   = require('web.Model');
var session = require('web.session');
var core    = require('web.core');
var screens = require('point_of_sale.screens');
var pos_models = require('point_of_sale.models');

var ScreenWidget = screens.ScreenWidget;
var PaymentScreenWidget = screens.PaymentScreenWidget;
var pos_order = pos_models.Order;
var _t = core._t;

PaymentScreenWidget.include({
    init: function(parent, options) {
        var self = this;
        this._super(parent, options);
        this.js_invoice_pending = false;
    },
    renderElement: function() {
        var self = this;
        this._super();

        this.$('.js_invoice_pending').click(function(){
            self.click_invoice_pending();
        });
    },
    validate_order: function(force_validation) {
        var self = this;
        var order = this.pos.get_order();

        if(this.$('.js_invoice_pending').hasClass('highlight') && this.$('.js_invoice').hasClass('highlight')){
            this.gui.show_popup('error',{
                'title': _t('Selection Issue'),
                'body':  _t('Select either Invoice or Invoice - Pending payment.'),
            });
            return false;
        }
        
        if (this.js_invoice_pending){
            if (order.get_orderlines().length === 0) {
                this.gui.show_popup('error',{
                    'title': _t('Empty Order'),
                    'body':  _t('There must be at least one product in your order before it can be validated'),
                });
                this._locked = true;
                return false;
            }
            this.to_invoice = true;
            var invoiced = this.finalize_validation(order)
            this.invoicing = true;
            this._locked = true;
            return true;
        }
        else{
            if (order.get_total_paid() == 0){
                this.gui.show_popup('error',{
                    'title': _t('Amount'),
                    'body':  _t('Please Select payment method and input amount'),
                });
                return false;
            }
//            if (this.order_is_valid(force_validation)) {
//
//                this.finalize_validation();
//            }
        }
        this._super(force_validation);
    },
    click_invoice: function(){
        if(this.$('.js_invoice_pending').hasClass('highlight')){
            this.gui.show_popup('error',{
                'title': _t('Selection Issue'),
                'body':  _t('Select either Invoice or Invoice - Pending payment.'),
            });
            return false;
        }
        var order = this.pos.get_order();
        order.set_to_invoice(!order.is_to_invoice());
        if (order.is_to_invoice()) {
            this.$('.js_invoice').addClass('highlight');
        } else {
            this.$('.js_invoice').removeClass('highlight');
        }
    },

    click_invoice_pending: function(){
        if(this.$('.js_invoice').hasClass('highlight')){
            this.gui.show_popup('error',{
                'title': _t('Selection Issue'),
                'body':  _t('Select either Invoice or Invoice - Pending payment.'),
            });
            return false;
        }
        var order = this.pos.get_order();
        order.set_to_invoice(!order.is_to_invoice());
        if (order.is_to_invoice()) {
            this.js_invoice_pending = true;
            this._locked = false;
            this.$('.next').addClass('highlight');
            this.$('.js_invoice_pending').addClass('highlight');
        } else {
            order.set_to_invoice(!order.is_to_invoice());

            this._locked = true;
            this.js_invoice_pending = false;
            this.$('.next').removeClass('highlight');
            this.$('.js_invoice_pending').removeClass('highlight');
        }
    },
});
});
