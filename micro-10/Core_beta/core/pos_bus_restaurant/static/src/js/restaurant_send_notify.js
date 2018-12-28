/**
 * Created by bruce on 3/23/17.
 */
odoo.define('pos_bus_restaurant_send_notify', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var floors = require('pos_restaurant.floors');
    var screens = require('point_of_sale.screens');
    var client_send_notify = require('client_send_notify');

    screens.OrderWidget.include({
        remove_orderline: function(order_line){
            var res = this._super(order_line);
            if (order_line.syncing == false || !order_line.syncing ) {
                let order = order_line.order.export_as_JSON();
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'line_removing',
                    data: {
                        uid: order_line.uid,
                    },
                    bus_id: this.pos.config.bus_id[0],
                    order: order,
                });
            }
            return res
        },
    });
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        set_table: function(table) {
            if (this.order_to_transfer_to_different_table && table) {
                var order_to_transfer_to_different_table = this.order_to_transfer_to_different_table;
                if (order_to_transfer_to_different_table.syncing == false || !order_to_transfer_to_different_table.syncing) {
                    order_to_transfer_to_different_table.syncing = true;
                    this.pos_bus.push_message_to_other_sessions({
                        action: 'order_transfer_new_table',
                        data: {
                            uid: order_to_transfer_to_different_table.uid,
                            table_id: table.id,
                            floor_id: table.floor_id[0],
                        },
                        order: order_to_transfer_to_different_table.export_as_JSON(),
                        bus_id: this.config.bus_id[0],
                    });
                    order_to_transfer_to_different_table.syncing = false;
                }
            }
            var res = _super_posmodel.set_table.apply(this, arguments);
            return res;
        },
    });
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            var self = this;
            _super_order.initialize.apply(this, arguments)
            this.bind('change', function(order) {
                self.pos.trigger('update:floor-screen')
            })
            this.orderlines.bind('change add remove', function(line) {
                self.pos.trigger('update:floor-screen')
            })
            if (this.pos.pos_bus) {
                this.bind('remove', function (order) {
                    var orders = self.pos.get('orders')
                    var other_order_the_same_table = orders.find(function (other_order) {
                        if (order.table && other_order.table && other_order.uid != order && order.table.id == other_order.table.id) {
                            return other_order;
                        }
                    })
                    if (other_order_the_same_table) {
                        if (other_order_the_same_table.syncing != true || !other_order_the_same_table.syncing) {
                            self.pos.pos_bus.push_message_to_other_sessions({
                                action: 're-sync-slip-order',
                                data: {
                                    uid: other_order_the_same_table.uid,
                                },
                                order: other_order_the_same_table.export_as_JSON(),
                                bus_id: this.pos.config.bus_id[0],
                            });
                        }
                    }

                })
            }
        },
        set_customer_count: function(count) { //sync to other sessions
            var res = _super_order.set_customer_count.apply(this, arguments)
            if (this.syncing == false || !this.syncing) {
                this.pos.pos_bus.push_message_to_other_sessions({
                    order: this.export_as_JSON(),
                    action: 'set_customer_count',
                    data: {
                        uid: this.uid,
                        count: count
                    },
                    bus_id: this.pos.config.bus_id[0],

                });
            }
            return res
        },
        saveChanges: function(){ //sync to other sessions
            var res = _super_order.saveChanges.apply(this, arguments)
            if (this.syncing == false || !this.syncing) {
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'request_printer',
                    data: {
                        uid: this.uid,
                    },
                    order: this.export_as_JSON(),
                    bus_id: this.pos.config.bus_id[0],
                });
            }
            return res;
        }
    });
    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_note: function(note){ //sync to other sessions
            var res = _super_order_line.set_note.apply(this, arguments)
            if (this.syncing == false || !this.syncing) {
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'set_note',
                    data: {
                        uid: this.uid,
                        note: note,
                    },
                    order: this.order.export_as_JSON(),
                    bus_id: this.pos.config.bus_id[0],
                });
            }
            return res;
        },
    })
})
