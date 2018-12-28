odoo.define('pos_sarangoci_modifier_layout.floors_extend', function (require) {
"use strict";

    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var floors = require('pos_restaurant.floors');
    var QWeb = core.qweb;
    var _t = core._t;

    var PrioButton = screens.ActionButtonWidget.extend({
        template: 'PrioButton',
        button_click: function() {
            var self = this;
            var user = this.pos.user.id;
            var order = this.pos.get_order();
            var line = this.pos.get_order().get_selected_orderline();
            line.is_priority = true;
            line.trigger("change", line);


        },
    });

    var CancelPrioButton = screens.ActionButtonWidget.extend({
        template: 'CancelPrioButton',
        button_click: function() {
            var self = this;
            var user = this.pos.user.id
            var order = this.pos.get_order();
            var line = this.pos.get_order().get_selected_orderline();
            line.is_priority = false;
            line.trigger("change", line);

        },
    });

    screens.define_action_button({
        'name': 'CancelPrioButton',
        'widget': CancelPrioButton
    });

    screens.define_action_button({
        'name': 'PrioButton',
        'widget': PrioButton
    });





});
