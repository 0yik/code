odoo.define('pos_untaxed_payment_method.main', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');


    models.load_fields('account.journal', ['usage_tax']);
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        after_load_server_data: function () {
            this.list_cashregister = this.cashregisters;
            this.update_cashregisters_tax(true);
            _super_posmodel.prototype.after_load_server_data.call(this);
        },
        update_cashregisters_tax: function (apply_tax) {
            this.cashregisters = this.list_cashregister.filter(function (item) {
               return  item.journal.usage_tax === (apply_tax ? 'taxed' : 'untaxed');
            });
            if(this.gui.screen_instances.payment){
                this.gui.screen_instances.payment.renderElement();
            }
        }
    });
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_apply_tax : function (apply_tax) {
            _super_order.set_apply_tax.apply(this,arguments);
            this.pos.update_cashregisters_tax(apply_tax);
        },
    });
});
