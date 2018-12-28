odoo.define('pos_sarangoci_config_receipt', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PaymentScreenWidget = screens.PaymentScreenWidget;
    var utils = require('web.utils');
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    models.load_fields("pos.config", "receipt_symbol");

    PosBaseWidget.include({
        format_currency : function (amount, precision) {
            if(this.pos && this.pos.currency && !this.pos.currency.position){
                return this.format_currency_no_symbol(amount,precision);
            }
            return this._super.apply(this, arguments);
        },
        format_currency_receipt : function (amount, precision) {
            if(this.pos && this.pos.config && this.pos.config.receipt_symbol) {
                return this.format_currency(amount, precision);
            }
            return this.format_currency_no_symbol(amount,precision);
        }
    });



});
