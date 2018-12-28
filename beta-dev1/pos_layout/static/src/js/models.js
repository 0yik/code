odoo.define('pos_layout.models', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    var QWeb = core.qweb;
    var _t = core._t;

    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            Order.initialize.apply(this,arguments);
            this.latest_order = this.latest_order || false;
            this.save_to_db();
        },
        add_product: function (product, options) {
            Order.add_product.call(this, product, options);
            var product_widget = this.pos.gui.screen_instances["products"];
            if(product_widget) product_widget.update_transaction_view();
        },
        get_total_tax: function() {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_tax();
            }
            ), 0), this.pos.currency.rounding);
        },
        set_client: function (client) {
            Order.set_client.call(this, client);
            var product_widget = this.pos.gui.screen_instances["products"];
            if(product_widget) product_widget.update_customer_view();
        },
        set_latest_time_order: function(time) {
            this.table.latest_order = time;
            this.trigger('change');
        },
        get_latest_time_order: function(){
            return this.table.latest_order;
        },
    });

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        set_table: function(table) {
            var res = _super_posmodel.set_table.apply(this, arguments);
            if(this.get_order()){
                this.gui.show_screen('products');
            }
            return res;
        },
    });

    // var Orderline = models.Orderline.prototype;
    // models.Orderline = models.Orderline.extend({
    //     init_from_JSON: function(json) {
    //         this.product = this.pos.db.get_product_by_id(json.product_id);
    //         if (!this.product) {
    //             return;
    //         }
    //         Orderline.initialize.apply(this,arguments);
    //     },
    // });
})