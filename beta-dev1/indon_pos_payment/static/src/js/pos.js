odoo.define('indon_pos_payment.pos', function (require) {
"use strict";

var screens = require('point_of_sale.screens')

screens.PaymentScreenWidget.include({
    payment_input: function(input) {
        if(input=='EXACT'){
            this._super('CLEAR')
            input = this.pos.get_order().get_total_with_tax()
            this._super(input)
        }
        else{
            this._super(input)
        }
    }
});

});

