odoo.define('modifier_honos_theme.load_pos_order', function(require){
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var rentals = require('pos_rental.pos_rental');


rentals.OrderScreenWidget.include({

    fetch_backend_pos_orders: function() {
        var self = this;
        var POSOrderModel = new Model('pos.order');
        var POSOrderLineModel = new Model('pos.order.line');

        POSOrderModel.query(['id', 'name', 'date_order', 'partner_id', 'lines', 'pos_reference','is_return_order','return_order_id','return_status', 'return_date', 'order_status', 'returned','collected','laundry','all_done', 'state', 'booking_id', 'start_date', 'end_date', 'invoice_id'])
            .filter([['id', 'not in', _.map(self.pos.db.pos_all_orders, function(ord) { return ord.id })], ['state', 'not in', ['cancel']]])
            .all()
            .then(function (ords) {
                _.each(ords, function(ord) {
                    self.pos.db.pos_all_orders.unshift(ord);
                });
            });
        POSOrderLineModel.query(['create_date','discount','display_name','id','order_id','price_subtotal','price_subtotal_incl','price_unit','product_id','qty','write_date','is_booked','is_ordered'])
            .filter([['id', 'not in', _.map(self.pos.db.pos_all_order_lines, function(line) { return line.id })]])
            .all()
            .then(function (lines) {
                _.each(lines, function(line) {
                    self.pos.db.pos_all_order_lines.unshift(line);
                });
            });
    },

    _get_backend_pos_orders: function() {
        this.fetch_backend_pos_orders();
    }
});

});