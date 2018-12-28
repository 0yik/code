odoo.define('delivery_orders_kds.pos_delivery', function (require) {
"use strict";

    var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
    var _t  = require('web.core')._t;

    OptionsPopupWidget.include({
        init: function(parent, args) {
            this._super(parent, args);
        },

        events: _.extend({}, OptionsPopupWidget.prototype.events, {
             'click .delivery_btn':  'dislay_delivery_popup',
        }),

        dislay_delivery_popup: function(){
            console.log("Delivery mode");
            // Fix: To show where it comes from In KDS screen
            this.pos.popup_option = 'Delivery'
            this.pos.category = 'delivery';
            var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
            if(this.pos.category != 'dive_in' && $CreateSalesOrderbutton){
                $CreateSalesOrderbutton.removeClass('oe_hidden');
            }
            this.gui.show_popup('deliveryoptionpopup', {
                'title': _t("LET'S GET STARTED"),
            });
        },
    });
});