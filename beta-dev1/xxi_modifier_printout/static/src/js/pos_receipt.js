odoo.define('xxi_modifier_printout.xxi_modifier_receipt', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var utils = require('web.utils');

    var QWeb = core.qweb;
    var _t = core._t;


    screens.ReceiptScreenWidget.include({
        print_xml: function () {
            var order = this.pos.get_order();
            var env = {
                widget: this,
                pos: this.pos,
                order: order,
                receipt: this.pos.get_order().export_for_printing(),
                orderlines: order.get_orderlines(),
                paymentlines: this.pos.get_order().get_paymentlines()
            };
            var receipt = QWeb.render('XmlReceipt', env);

            this.pos.proxy.print_receipt(receipt);
            this.pos.get_order()._printed = true;
        },
    });

});

