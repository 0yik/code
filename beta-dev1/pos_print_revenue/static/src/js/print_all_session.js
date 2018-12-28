odoo.define('pos_print_revenue.print_all_session', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var QWeb = core.qweb;
    // Generates a report to print the sales of the
    // day on a ticket
    var PrintMultiSessionButton = chrome.StatusWidget.extend({
        template: 'PrintMultiSessionButton',
        start: function(){
            var self = this;
            this.$el.click(function(){
                console.log("click click");
                self.print_xml();
            });
        },
        print_xml: function() {
            var self = this;
            var model = new Model('pos.order');
            model.call("get_orders_session_today", [this.pos.pos_session.id]).then(function (result) {
                console.log("alibaba click");
                var env = {
                    'widget' : self,
                    'data' : result,
                }
                var receipt = QWeb.render('XmlPrintMultiSessionReceipt', env);
                var printers = self.pos.printers;
                var pos = self.pos;
                for (var i = 0; i < printers.length; i++) {
                    pos.printers.pop(printers[i]);
                    pos.printers.pop(printers[i]);
                    pos.proxy.print_receipt(receipt);
                }
            });
        }
    });
    chrome.SynchNotificationWidget.include({
        renderElement: function(){
            new PrintMultiSessionButton(this, {}).appendTo('.pos-rightheader');
            this._super();
        }
    });

});
