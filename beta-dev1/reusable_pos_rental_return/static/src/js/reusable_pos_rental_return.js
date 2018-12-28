odoo.define('reusable_pos_rental_return.reusable_pos_rental_return', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');
var PosRental = require('pos_rental.pos_rental')

var _t = core._t;


PosRental.OrderScreenWidget.include({

    show: function() {
        var self = this;
        this._super();

        // unbinding click event and binding it again with modification
        this.$('.wk_returned').off('click');
        this.$('.wk_returned').click(function(options) {
            var order_id = this.id;
            var index = false;
            _.each(self.pos.db.pos_all_orders, function(order, idx) {
                if (order.id == order_id) {
                    index = idx;
                }
            });
            var order = self.pos.db.pos_all_orders[index];
            if(order && order.collected && !order.returned) {
                var orig_this = this;
                var orig_self = self;
                var allow_return = true;
                var end_date = moment(order.end_date);
                var today = moment().format('YYYY-MM-DD');

                if (end_date.isAfter(today)) {
                    allow_return = false;
                    self.pos.gui.show_popup('confirm',{
                        'title': _t('Early return'),
                        'body':  _t("You’re rental period is not over. Would you like to return today?"),
                        confirm: function(){
                            self.pos.gui.show_popup('return-product-screen', {'order_id': order_id, 'confirm': self.perform_operation, 'orig_this': orig_this, 'orig_self': orig_self, 'orig_action': 'returned'});
                        },
                    });
                }
                if (allow_return) {
                    self.pos.gui.show_popup('return-product-screen', {'order_id': order_id, 'confirm': self.perform_operation, 'orig_this': orig_this, 'orig_self': orig_self, 'orig_action': 'returned'});
                }
            } else {
                if (order) {
                    self.pos.gui.show_popup('error', {
                        'title': _t('Not Allowed !!!'),
                        'body': _t("Cannot perform this operation.")
                    });
                }
            }
        });
    },

});

});
