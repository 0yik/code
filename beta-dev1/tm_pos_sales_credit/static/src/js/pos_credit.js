odoo.define('tm_pos_sales_credit.pos_credit', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');

    var QWeb = core.qweb;
    var _t  = require('web.core')._t;

    models.load_fields('res.partner', ['credit','credit_limit','over_credit','trust']);
    // models.load_fields('res.partner', ['credit', 'credit_limit']);
    screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
        },
        show: function () {
            var self = this;
            this._super();
            if(this.pos.get_order().get_client()){
                this.$('.sale-debit').text(this.pos.get_order().get_client().name + ' Debit Payment');
                this.$('.sale-debit-customer').off().click(function(){
                    var order  = self.pos.get_order();
                    var client = order.get_client();
                    var due    = order.get_due();
                    var residual = client.credit_limit - client.credit;
                    if (client.over_credit){
                        self.add_payment_debit();
                    }else{
                        if(residual >= due){
                            self.add_payment_debit();
                        }else{
                            alert('Transaction over credit, please payment debit');
                        }
                    }
                });
            }else{
                this.$('.sale-debit').text('Customer Debit Payment');
                this.$('.sale-debit-customer').off().click(function(){
                    self.gui.show_screen('clientlist');
                });
            }
        },
        add_payment_debit: function () {
            var self = this;
            var order  = self.pos.get_order();
            var due    = order.get_due();
            var cashregister = Object.assign({}, self.pos.cashregisters[0]);
            cashregister.journal_id[1] = "Payment debit";
            order.add_paymentline( cashregister );
            order.paymentlines.models[order.paymentlines.length - 1].amount = due;
            order.payment_debit = due;
            self.gui.screen_instances.payment.reset_input();
            self.gui.screen_instances.payment.render_paymentlines();
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.call(this);
            json.payment_debit = this.payment_debit;
            return json
        },
        init_from_JSON: function(json) {
            this.payment_debit = json.payment_debit;
            _super_order.init_from_JSON.call(this, json);
        },

    });
});