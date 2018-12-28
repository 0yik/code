odoo.define('pos_payment_creditcard.models', function (require) {

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    models.load_fields('account.journal', ['need_input', 'min_digits', 'max_digits']);

    screens.PaymentScreenWidget.include({
        click_paymentmethods: function(id) {
            var cashregister = null;
            var self = this
            for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
                if ( this.pos.cashregisters[i].journal_id[0] === id ){
                    cashregister = this.pos.cashregisters[i];
                    break;
                }
            }
            console.log('cash registerrrr',cashregister)
            if(cashregister.journal.need_input){
                self.pos.gui.show_popup('number', {
                        'title':  _t('Enter CREDITCARD Number'),
                        'cheap': true,
                        'value': '',
                        'confirm': function(value) {
                            var pin = $('.popup-input').text().trim();
                            if(!pin.trim()){
                                alert('Please Enter PIN First!')
                                return false
                            }
                            else{
                                if(pin.length>=cashregister.journal.min_digits && pin.length<=cashregister.journal.max_digits){
                                    self.pos.get_order().payment_ref = pin;
                                
                                }else{
                                    alert('Enter number of digits between '+cashregister.journal.min_digits+' and '+cashregister.journal.max_digits)
                                    return false
                                }                                
                            }
                        },
                        'cancel': function(){
                             return false
                        }
                    });
            }
            this._super(id);       
        },
    });
    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            Order.initialize.apply(this, arguments); 
        },
        init_from_JSON: function(json) {
            Order.init_from_JSON.apply(this,arguments);
            this.payment_ref = json.payment_ref;
        },
        export_as_JSON: function() {
            var ret=Order.export_as_JSON.call(this);
            ret.payment_ref = this.payment_ref;
            return ret;
        },
    });
  
});