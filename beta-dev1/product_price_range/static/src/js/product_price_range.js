odoo.define('product_price_range.product_price_range', function (require) {
    "use strict";
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var utils = require('web.utils');
    var formats = require('web.formats');

    var QWeb = core.qweb;
    var _t = core._t;
    var check_error = false;

    var round_pr = utils.round_precision;

    screens.OrderWidget.include({
        template: 'OrderWidget',
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);

            this.numpad_state = options.numpad_state;
            this.numpad_state.reset();
            this.numpad_state.bind('set_value', this.set_value, this);

            this.pos.bind('change:selectedOrder', this.change_selected_order, this);

            this.line_click_handler = function (event) {
                self.click_line(this.orderline, event);
            };

            if (this.pos.get_order()) {
                this.bind_order_events();
            }
        },
        click_line: function (orderline, event) {
        	console.log('test')
            this.show_popup_warning();
            this.pos.get_order().select_orderline(orderline);
            this.numpad_state.reset();
        },
        orderline_add: function () {
            this.numpad_state.reset();
            this.renderElement('and_scroll_to_bottom');
            this.show_popup_warning();
        },
        set_value: function (val) {
            var self = this
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if (mode === 'quantity') {
                    order.get_selected_orderline().set_quantity(val);
                } else if (mode === 'discount') {
                    order.get_selected_orderline().set_discount(val);
                } else if (mode === 'price') {
                    order.get_selected_orderline().set_unit_price(val);
                    var data = $.ajax({
                        url: "/api/product_range",
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({
                            product_id: order.get_selected_orderline().product.product_tmpl_id,
                            order_line : 1
                        }),
                        success: function (result) {
                            console.log('test')
                            if (order.get_selected_orderline().price > result[0].max_sale_price) {
                                var warning = "Unit Price is out of range (from: $"+ result[0].min_sale_price + " to: $"+ result[0].max_sale_price +")"
                                self.gui.show_popup('error', {
                                    title: _t('Warning'),
                                    body: _t(warning),
                                });
                            }
                        }
                    });
                }
            }
        },
        show_popup_warning: function () {
            var self = this;
            var order = self.pos.get_order();
            var order_line_ids = order.orderlines.models
            for (var i = 0; i<order_line_ids.length; i++) {
                var order_line_id = order_line_ids[i]
                $.ajax({
                    url: "/api/product_range",
                    type: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({
                        product_id: order_line_id.product.product_tmpl_id,
                        order_line : i,
                    }),
                    success: function (result) {
                        if (order_line_ids[result[0].order_line].price < result[0].min_sale_price || order_line_ids[result[0].order_line].price > result[0].max_sale_price) {
                            self.pos.get_order().select_orderline(order_line_ids[result[0].order_line]);
                            var warning = "Unit Price is out of range (from: $"+ result[0].min_sale_price + " to: $"+ result[0].max_sale_price +")"
                            self.gui.show_popup('error', {
                                title: _t('Warning'),
                                body: _t(warning),
                            });
                        }
                    }
                });
            }
        },
    });

    screens.ActionpadWidget.include({
    template: 'ActionpadWidget',

    renderElement: function() {
        var self = this;
        this._super();
        this.$('.pay').click(function(){
            self.check_error = false;
            self.show_popup_warning();
	    var order = self.pos.get_order();
	    var issuer = order.get_issuer();
            setTimeout(function(){
                if (!self.check_error){
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                console.log('error payment')
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
		    if(!issuer){
			self.gui.show_screen('products');
		        return;
		    }
		    else{
                self.gui.show_screen('payment');
		    }
                }
            }
            else {
                self.gui.show_screen('products');
                self.gui.show_popup('error', {
                                title: _t('Warning'),
                                body: _t(self.check_error),
                            });
            }
            }, 100);
        });
    },
    show_popup_warning: function () {
            var self = this;
            var order = self.pos.get_order();
            var order_line_ids = order.orderlines.models;
            for (var i = 0; i<order_line_ids.length; i++) {
                var order_line_id = order_line_ids[i];
                console.log('test')
                $.ajax({
                    url: "/api/product_range",
                    type: 'POST',
                    dataType: 'json',
                    data: JSON.stringify({
                        product_id: order_line_id.product.product_tmpl_id,
                        order_line : i,
                    }),
                    success: function (result) {
                        if (order_line_ids[result[0].order_line].price < result[0].min_sale_price || order_line_ids[result[0].order_line].price > result[0].max_sale_price) {
                            self.pos.get_order().select_orderline(order_line_ids[result[0].order_line]);
                            var warning = "Product '" + order_line_ids[result[0].order_line].product.display_name + "' Unit Price is out of " +
                                "range (from: $"+ result[0].min_sale_price + " to: $"+ result[0].max_sale_price +")";
                            self.check_error = warning;
                        }
                    }
                });
            }
        },
});

});

