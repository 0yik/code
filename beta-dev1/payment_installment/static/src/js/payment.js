odoo.define('payment_installment.payment', function (require) {
'use strict';
    var session = require('web.session');
    var FormView = require('web.FormView');
    var ListView = require('web.ListView');
    var Model = require('web.Model');

    FormView.include({
        load_record: function(record) {
            var self = this;
            var result = this._super(record);
            if(record.payment_installment_type){
                let list_option_hide = ['all','percentage','fixed'];
                list_option_hide.forEach(function (item) {
                    self.$('input[type="radio"][value="'+item+'"]').parent().hide();
                })
            }
            return result;
        },
    });
});