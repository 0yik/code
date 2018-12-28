odoo.define('bom_pos_modifier.pos', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screenps = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var Model = require('web.Model');
    var Order = models.Order.prototype
    models.Order = models.Order.extend({
        initialize_validation_date: function () {
            Order.initialize_validation_date();
            for (var k = 0; k < this.orderlines.models.length; k++) {
            	var doneline = this.orderlines.models[k];
                var order_line = doneline.export_as_JSON();
                order_line['pos_session_id'] = this.pos_session_id
                new Model("pos.order").call("reduce_bom_stock", [[]],{'order_line':JSON.stringify(order_line)}).then(function(results){
                    // sort activities by due date
                });
            }
//            return this._super();
        }
    });
});

