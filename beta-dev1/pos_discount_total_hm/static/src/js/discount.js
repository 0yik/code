odoo.define('pos_discount_total_hm.pos_discount_total_hm', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var gui     = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');
var core = require('web.core');
var utils = require('web.utils');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var round_pr = utils.round_precision;
var QWeb     = core.qweb;
var Widget = require('web.Widget');

screens.OrderWidget.include({

    });
var _super = models.Order;
models.Order = models.Order.extend({
    is_payment: function () {
        var discount = this.discount ? this.discount : 0 ;
        return (discount > this.get_total_without_tax()*0.2) ? false : true;
    },
    get_discount: function () {
        return this.discount ? this.discount : 0 ;
    },
    get_total_with_discount_and_tax: function () {
        return this.get_total_with_tax() - this.get_discount();
    },
    get_change: function(paymentline) {
            if (!paymentline) {
                var change = this.get_total_paid() - this.get_total_with_discount_and_tax();
            } else {
                var change = -this.get_total_with_discount_and_tax();
                var lines = this.paymentlines.models;
                for (var i = 0; i < lines.length; i++) {
                    change += lines[i].get_amount();
                    if (lines[i] === paymentline) {
                        break;
                    }
                }
            }
            return round_pr(Math.max(0, change), this.pos.currency.rounding);
        },
    get_due: function(paymentline) {
        if (!paymentline) {
            var due = this.get_total_with_discount_and_tax() - this.get_total_paid();
        } else {
            var due = this.get_total_with_discount_and_tax();
            var lines = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                if (lines[i] === paymentline) {
                    break;
                } else {
                    due -= lines[i].get_amount();
                }
            }
        }
        return round_pr(Math.max(0, due), this.pos.currency.rounding);
    },
    order_is_valid: function(force_validation) {
        var self = this;
        var order = this.pos.get_order();
        if (order.get_orderlines().length === 0) {
            this.gui.show_popup('error', {
                'title': _t('Empty Order'),
                'body': _t('There must be at least one product in your order before it can be validated'),
            });
            return false;
        }
        var plines = order.get_paymentlines();
        for (var i = 0; i < plines.length; i++) {
            if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                this.gui.show_popup('error', {
                    'message': _t('Negative Bank Payment'),
                    'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                });
                return false;
            }
        }
        if (!order.is_paid() || this.invoicing) {
            return false;
        }
        if (Math.abs(order.get_total_with_discount_and_tax() - order.get_total_paid()) > 0.00001) {
            var cash = false;
            for (var i = 0; i < this.pos.cashregisters.length; i++) {
                cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
            }
            if (!cash) {
                this.gui.show_popup('error', {
                    title: _t('Cannot return change without a cash payment method'),
                    body: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                });
                return false;
            }
        }
        if (!force_validation && order.get_total_with_discount_and_tax() > 0 && (order.get_total_with_discount_and_tax() * 1000 < order.get_total_paid())) {
            this.gui.show_popup('confirm', {
                title: _t('Please Confirm Large Amount'),
                body: _t('Are you sure that the customer wants to  pay') + ' ' + this.format_currency(order.get_total_paid()) + ' ' + _t('for an order of') + ' ' + this.format_currency(order.get_total_with_tax()) + ' ' + _t('? Clicking "Confirm" will validate the payment.'),
                confirm: function() {
                    self.validate_order('confirm');
                },
            });
            return false;
        }
        return true;
    },
    export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
        if (this.discount && this.get_client()) {
            json.discount = this.get_discount();
            json.grand_total = this.get_total_with_discount_and_tax();
        }
        return json;
    },

    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.discount = this.get_discount();
        json.grand_total = this.get_total_with_discount_and_tax();
        return json;
    },
});
screens.OrderWidget.include({
    update_summary: function () {
        this._super();
        var order = this.pos.get_order();
        var grand_total = order ? order.get_total_with_discount_and_tax() : 0;
        var total = order ? order.get_total_without_tax() : 0;
        var untaxed_amount = order ? order.get_total_without_tax() - order.get_discount() : 0;
        var sumary_total = this.el.querySelector('.summary .total > .value');
        if(sumary_total){
            sumary_total.textContent = this.format_currency(total);
        }
        $('div.summary .untax_amount > .amount').text(this.format_currency(untaxed_amount));
        $('div.summary .grand_total > .value').text(this.format_currency(grand_total));
    },
    rerender_orderline: function (order_line) {
        try {
            this._super(order_line);
        } catch (e) {
            console.error(e);
        }
    },
});

gui.Gui = gui.Gui.extend({
    show_screen: function(screen_name,params,refresh) {
        var self = this;
        var order = self.pos.get_order();
        if( !order.is_payment() ){
            screen_name = 'products';
        }
        self._super(screen_name,params,refresh);
    }
});
var ActionpadWidget = PosBaseWidget.include({
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.pay').click(function() {
            var order = self.pos.get_order();
            if( !order.is_payment() ){
                //alert("Discount can't be greater than 20% of total!\n( $ " + order.get_total_without_tax()*0.2 + ")");
                alert("Overdiscount");
                return;
            }
        });
    }
});

var DiscountButton = screens.ActionButtonWidget.extend({
    template: 'DiscountButton',
    button_click: function(){
        console.log('Click');
        this.gui.show_popup('discount_total',{});
     },
});

screens.define_action_button({
    'name': 'discount',
    'widget': DiscountButton,
    'condition': function(){
        return true;
    },
});
var DiscountPopupWidget = PopupWidget.extend({
	    template: 'DiscountPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
	        'click .paymentline-delete': 'reset_discount',
	        'change .paymentline-input': 'update_discount',
	        'keyup input.paymentline-input': 'update_discount',
	    }),
	    show: function(options){
	    	options = options || {};
	        this._super(options);
	        console.log(options);
    		this.renderElement();
	    },
	    click_confirm: function(){
            var self = this;
			var discount = $('#discount_input').val();
			var order = this.pos.get('selectedOrder');

			console.log(discount, order.amount_total);
            if (order) {
                var amount_total = 0.0;
                var total = 0.0;
                var order_lines = order.orderlines.models;
                for (var x = 0; x < order_lines.length; x++) {
                    amount_total += order_lines[x].get_price_with_tax();
                    total += order_lines[x].get_price_without_tax();
                }
                if(discount > total*0.2) {
                    alert("Discount can't be greater than 20% of total!\n( " + this.format_currency(total*0.2) + ")");
                    return;
                }
                order.discount = discount;
                order.grand_total = grand_total;
                var grand_total = amount_total - discount;
                $('div.discount .value').text(this.format_currency(discount));
                $('div.summary .untax_amount > .amount').text(this.format_currency(total-discount));
                $('div.summary .grand_total > .value').text(this.format_currency(grand_total));
            }
	        this.gui.close_popup();
	    },
	    click_cancel: function(){
			this.gui.close_popup();
	    },
        reset_discount: function(){
			$('.paymentline-input').val('0.00');
			$('.payment-due-total').text('$ 0.00');
	    },
        update_discount: function(){
            $('.payment-due-total').text('$ ' + $('.paymentline-input').val());
        },
	});
gui.define_popup({name:'discount_total', widget: DiscountPopupWidget});
});
