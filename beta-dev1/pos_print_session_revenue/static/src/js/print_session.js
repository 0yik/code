odoo.define('pos_print_session_revenue.print_session', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var QWeb = core.qweb;
    // Generates a report to print the sales of the
    // day on a ticket
    var PrintSessionButton = chrome.StatusWidget.extend({
        template: 'PrintSessionButton',
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
            model.call("get_orders_today", [this.pos.pos_session.id]).then(function (result) {
                console.log("alibaba click");
                var env = {
                    'widget' : self,
                    'data' : result,
                }
                var receipt = QWeb.render('XmlPrintSessionReceipt', env);
                var printers = self.pos.printers;
                var pos = self.pos;
                for (var i = 0; i < printers.length; i++) {
                    pos.printers.pop(printers[i]);
                    pos.printers.pop(printers[i]);
                    pos.proxy.print_receipt(receipt);
                }
            });


        },
        print_web: function() {
            window.print();
            this.pos.get_order()._printed = true;
        },
        print: function() {
            var self = this;
            if (!this.pos.config.iface_print_via_proxy) {
                this.lock_screen(true);
                setTimeout(function() {}, 1000);
                this.print_web();
            } else {
                console.log('print_xml');
                this.print_xml();
            }
        },
    });
    chrome.SynchNotificationWidget.include({
        renderElement: function(){
            $('.pos-rightheader .fa-print').first().parent().hide();
            new PrintSessionButton(this, {}).appendTo('.pos-rightheader');
            this._super();
        }
    });

});
