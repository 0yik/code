odoo.define('pos_service_charge_all_free.pos_service_charge_all_free', function (require) {
"use strict";

var all_free = require('pos_all_free.pos')
var service_charge = require('pos_product_service_charge.pos_service_charge')

all_free = all_free.include({
    button_click: function() {
        this._super();
        var order = this.pos.get_order();
        if(order.all_free && order.service_charge){
            $('.service-charge-button').trigger('click');
        }
    },
});
service_charge = service_charge.include({
    button_click: function() {
        var order = this.pos.get_order();
        if(order.all_free && !order.service_charge){
            alert('When All Free is set, Service Charge can not be enabled.');
        }
        else{this._super();}
    },
});
});