odoo.define('inventory_on_purchase.purchase_order_line', function (require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var ListView = require('web.ListView');
    var Model = require('web.Model');
    FormView.include({
        load_record: function (record) {
            var self = this;
            self._super.apply(self, arguments);
        console.log('log1');
        // if (self.model == 'purchase.order.line') {
        //     console.log('log1');
        //     setTimeout(function () {
        //         $("div.div_width").css("width", "50%");
        //     }, 500);
        //     setTimeout(function () {
        //         $("div.product_uom_width").css("width", "50%");
        //     }, 500);
        // }
        }
    });
});