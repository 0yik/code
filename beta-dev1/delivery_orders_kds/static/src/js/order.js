odoo.define('delivery_orders_kds.order', function (require) {
"use strict";

    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var _t = core._t;
    var ListInvoiceButton = screens.ActionButtonWidget.extend({
        'template': 'ListInvoiceButton',
        button_click: function(){
            this.gui.show_popup('deliveryoptionpopup', {
                'title': _t("LET'S GET STARTED"),
            });
        },
    });
    screens.define_action_button({
        'name': 'list_invoice',
        'widget': ListInvoiceButton,
        'condition': function() {
            return true;
        },
    });
});

