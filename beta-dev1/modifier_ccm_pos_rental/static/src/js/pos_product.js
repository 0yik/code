odoo.define('modifier_ccm_pos_rental.pos_product', function(require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');

screens.ProductScreenWidget.include({
    start: function() {
        this._super();

        // move all order, today order and deposit button on top
        var $control_buttons = this.$('.control-buttons');
        var $first_element = $control_buttons.children().first();
        var $today_orders = $control_buttons.find('#today_orders');
        var $all_orders = $control_buttons.find('#all_orders');
        var $deposit_button = $control_buttons.find('#deposit_button');

        $today_orders.insertBefore($first_element);
        $all_orders.insertBefore($first_element);
        $deposit_button.insertBefore($first_element);

        var $last_element = $control_buttons.children().last();
        var $auto_promotion = $control_buttons.find('.auto-promotion');
        $auto_promotion.insertAfter($last_element);
    },
});
});
