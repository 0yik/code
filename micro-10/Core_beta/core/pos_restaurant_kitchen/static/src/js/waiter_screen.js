odoo.define('pos_restaurant_kitchen_screen', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    screens.OrderWidget.include({ // sync from waiter to kitchen
        render_orderline: function (orderline) {
            var self = this;
            var el_node = this._super(orderline);
            var cancel_button = el_node.querySelector('.cancel');
            if (cancel_button) {
                cancel_button.addEventListener('click', function () {
                    orderline.set_state('Cancel');
                });
            }
            var done_button = el_node.querySelector('.done');
            if (done_button) {
                done_button.addEventListener('click', function () {
                    orderline.set_state('Done');
                });
            }
            var error_button = el_node.querySelector('.error');
            if (error_button) {
                error_button.addEventListener('click', function () {
                    orderline.set_state('Error');
                });
            }
            var priority_button = el_node.querySelector('.priority');
            if (priority_button) {
                priority_button.addEventListener('click', function () {
                    orderline.set_state('High-Priority');
                });
            }
            var confirm_button = el_node.querySelector('.confirm');
            if (confirm_button) {
                confirm_button.addEventListener('click', function () {
                    orderline.set_state('Confirmed');
                });
            }
            var put_back_button = el_node.querySelector('.put-back');
            if (put_back_button) {
                put_back_button.addEventListener('click', function () {
                    orderline.set_state('Waiting-delivery');
                });
            }
            return el_node;

        },
    })
    var ButtonHighPriority = screens.ActionButtonWidget.extend({
        template: 'ButtonHighPriority',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state != 'Kitchen confirmed cancel' && line.state != 'Done' && line.state != 'Cancel' && line.state != 'Error' && line.state != 'Waiting-delivery') {
                        line.set_state('High-Priority');
                    }
                }
            }
        },
    });
    screens.define_action_button({
        'name': 'ButtonHighPriority',
        'widget': ButtonHighPriority,
        'condition': function () {
            return this.pos.config.screen_type == 'waiter' || this.pos.config.screen_type == 'manager';
        }
    });
    var ButtonExitHighPriority = screens.ActionButtonWidget.extend({
        template: 'ButtonExitHighPriority',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line && line.state && line.state == 'High-Priority') {
                        line.set_state('Confirmed');
                    }
                }
            }
        },
    });
    screens.define_action_button({
        'name': 'ButtonExitHighPriority',
        'widget': ButtonExitHighPriority,
        'condition': function () {
            return this.pos.config.screen_type == 'waiter' || this.pos.config.screen_type == 'manager';
        }
    });

    var ButtonConfirm = screens.ActionButtonWidget.extend({
        template: 'ButtonConfirm',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line && line.state && line.state == 'Need-to-confirm') {
                        line.set_state('Confirmed');
                    }
                }
            }
            $('.order-submit').click();
        },
    });
    screens.define_action_button({
        'name': 'ButtonConfirm',
        'widget': ButtonConfirm,
        'condition': function () {
            return this.pos.config.screen_type == 'waiter';
        }
    });

    var ButtonDoneAll = screens.ActionButtonWidget.extend({
        template: 'ButtonDoneAll',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state == 'Waiting-delivery') {
                        line.set_state('Done');
                    }
                }
            }
        },
    });
    screens.define_action_button({
        'name': 'ButtonDoneAll',
        'widget': ButtonDoneAll,
        'condition': function () {
            return this.pos.config.screen_type == 'waiter' || this.pos.config.screen_type == 'manager';
        }
    });
})