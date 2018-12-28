odoo.define('pos_user_access.pos_user_access', function (require) {
"use strict";

var chrome = require('point_of_sale.chrome');
var core = require('web.core');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');

var _t = core._t;
var _lt = core._lt;


models.load_fields('res.users', ['pos_access_close', 'pos_access_delete_order',
                                 'pos_access_delete_orderline', 'pos_access_decrease_quantity',
                                 'pos_access_discount', 'pos_access_payment', 'pos_access_price', 'pos_access_minus'])

chrome.OrderSelectorWidget.include({
    deleteorder_click_handler: function(event, $el) {
        var user = this.pos.get_cashier();
        if (!user.pos_access_delete_order) {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to delete an order!'),
            });
        } else {
            this._super(event, $el);
        }
    },
});

chrome.Chrome.include({
    build_widgets: function() {
        for (var i = 0; i < this.widgets.length; i++) {
            var widget = this.widgets[i];
            if (widget.name === 'close_button') {
                widget.args = {
                    label: _lt('Close'),
                    action: function() {
                        var self = this;
                        if (!this.confirmed) {
                            this.$el.addClass('confirm');
                            this.$el.text(_t('Confirm'));
                            this.confirmed = setTimeout(function() {
                                self.$el.removeClass('confirm');
                                self.$el.text(_t('Close'));
                                self.confirmed = false;
                            }, 2000);
                        } else {
                            this.gui.close(this);
                        }
                    },
                }
            }

        }
        this._super();
    },
});

models.NumpadState = models.NumpadState.extend({
    appendNewChar: function(newChar) {
        var oldBuffer = this.get('buffer');
        if (oldBuffer === '0') {
            var buffer = newChar;
        } else if (oldBuffer === '-0') {
            var buffer = '-' + newChar;
        } else {
            var buffer = (this.get('buffer')) + newChar;
        }
        this.trigger('set_value', buffer);
    },
});

screens.OrderWidget.include({
    set_value: function(val) {
        var mode = this.numpad_state.get('mode');
        var order = this.pos.get_order();
        var orderline = order.get_selected_orderline();
        var user = this.pos.get_cashier();

        if (!user.pos_access_decrease_quantity && orderline && mode === 'quantity'
                && parseFloat(orderline.quantity) > parseFloat(val)) {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to decrease the quantity of an order line!'),
            });
        } else {
            this.numpad_state.set({'buffer': val})
            this._super(val);
        }
    },
});

screens.NumpadWidget.include({
    clickDeleteLastChar: function(event) {
        var buffer = this.state.get('buffer');
        var mode = this.state.get('mode');
        var user = this.pos.get_cashier();
        if (!user.pos_access_delete_orderline && buffer === '' && mode === 'quantity') {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to delete an order line!'),
            });
        } else if (!user.pos_access_decrease_quantity && buffer !== '' && mode === 'quantity') {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to decrease the quantity of an order line!'),
            });
        } else {
            this._super();
        }
    },
    clickSwitchSign: function(event) {
        var user = this.pos.get_cashier();
        var order = this.pos.get_order();
        var mode = this.state.get('mode');
        var orderline = order.get_selected_orderline();
        if((orderline.quantity >= 0 && mode === 'quantity') || (orderline.price >= 0 && mode === 'price')){
            if (!user.pos_access_minus) {
                this.gui.show_popup('error', {
                    title: _t('Access Denied'),
                    body: _t('You do not has access to apply minus function!'),
                });
            }
            else{
                this._super();
            }
        }
        else {
            this._super();
        }
    },
    clickChangeMode: function(event) {
        var newMode = event.currentTarget.attributes['data-mode'].value;
        var user = this.pos.get_cashier();
        if (!user.pos_access_discount && newMode === 'discount') {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to apply discount!'),
            });
        } else if (!user.pos_access_price && newMode === 'price') {
            this.gui.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to change price!'),
            });
        } else {
            this._super(event);
        }
    },
});

gui.Gui.include({
    close: function(close_button) {
        var user = this.pos.get_cashier();
        if (!user.pos_access_close) {
            this.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to close a POS!'),
            });
        } else {
            clearTimeout(close_button.confirmed);
            this._super();
        }
    },

    show_screen: function(screen_name, params, refresh, skip_close_popup) {
        var user = this.pos.get_cashier();
        if (!user.pos_access_payment && screen_name === 'payment') {
            this.show_popup('error', {
                title: _t('Access Denied'),
                body: _t('You do not have access to apply payment!'),
            });
        } else {
            this._super(screen_name, params, refresh, skip_close_popup);
        }
    },
});


});
