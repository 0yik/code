odoo.define('pos_so_payments.so_payment_btn', function (require) {
"use strict";

    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var _t = core._t;
    var ListSOButton = screens.ActionButtonWidget.extend({
        'template': 'ListSOButton',
        button_click: function(){
            this.gui.show_screen('list_so_screen');
        },
    });
    screens.define_action_button({
        'name': 'list_so',
        'widget': ListSOButton,
        'condition': function() {
            return true;
        },
    });
});

