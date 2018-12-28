odoo.define('modifier_ccm_pos_rental.pos_receipt', function(require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var screens = require('point_of_sale.screens');
var QWeb = core.qweb;

screens.ReceiptScreenWidget.include({
    fetch_invoice_id: function() {
        var invoiced = new $.Deferred()
        var order = this.pos.get_order();
        if (order.to_invoice) {
            invoiced = new Model('pos.order').call('search_read', [[['pos_reference', '=', order.name]], ['invoice_id']]).then(function(res) {
                if (res.length > 0) {
                    order.invoice_id = res[0].invoice_id;
                }
            });
        } else {
            invoiced.resolve();
        }
        return invoiced;
    },
    render_receipt: function() {
        var self = this;
        var order = this.pos.get_order();
        this.fetch_invoice_id().then(function() {
            self.$('.pos-receipt-container').html(QWeb.render('PosTicket',{
                    widget:self,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                }));
        })
    },

});
});
