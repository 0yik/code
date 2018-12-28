odoo.define('sale.view_quotation_tree', function (require) {
"use strict";

    var ListView = require('web.ListView');
    var Model = require('web.Model');
    var session = require('web.session');

    ListView.include({
        render_buttons: function () {
            var self = this;
            console.log('1');
            if (this.model == 'sale.order') {
                self = this;
                var action = self.dataset.context.params.action;
                new Model('sale.order').call('check_action', [action]).then(function (check_action) {
                    if (check_action == 'quotation') {
                        setTimeout(function() {
                             $(".btn-group ul li a:contains('Joining Invoice')").hide();
                             $(".btn-group ul li a:contains('Joining Sales Order')").show();
                            },200);
                    }
                    else if (check_action == 'sale') {
                        setTimeout(function() {
                             $(".btn-group ul li a:contains('Joining Invoice')").show();
                             $(".btn-group ul li a:contains('Joining Sales Order')").hide();
                            },200);
                    }
                });
            }
            this._super.apply(this, arguments); // Sets this.$buttons
        },
    });
});

// odoo.define('sale.view_order_tree', function (require) {
// "use strict";
//
//     var ListView = require('web.ListView');
//     var Model = require('web.Model');
//     var session = require('web.session');
//
//     ListView.include({
//         render_buttons: function () {
//             var self = this;
//             console.log('2');
//             if (this.model == 'sale.order') { // Ensures that this is only done once
//                 setTimeout(function() {
//                  $(".btn-group ul li a:contains('Joining Invoice')").show();
//                  $(".btn-group ul li a:contains('Joining Sales Order')").hide();
//                 },200);
//             }
//             this._super.apply(this, arguments); // Sets this.$buttons
//         },
//     });
// });
odoo.define('sale.view_order_form', function (require) {
'use strict';
    var session = require('web.session');
    var FormView = require('web.FormView');
    var ListView = require('web.ListView');
    var Model = require('web.Model');

    FormView.include({
        load_record: function(record) {
            var self = this;
            console.log('321');
            self._super.apply(self, arguments);
            if (self.model == 'sale.order') {
                setTimeout(function() {
                 $(".btn-group ul li a:contains('Joining Invoice')").hide();
                 $(".btn-group ul li a:contains('Joining Sales Order')").hide();
                },200);

            }
        },
    });
});