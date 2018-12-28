odoo.define('pos_bus_restaurant_get_notify', function (require) {
    "use strict";
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var chrome = require('point_of_sale.chrome');
    var syncing = require('client_get_notify');
    var multiprint = require('pos_restaurant.multiprint')

    models.load_models({
        model: 'restaurant.floor',
        fields: ['name','background_color','table_ids','sequence'],
        domain: function(self){ return [['id','in',self.config.floor_ids]]; },
        loaded: function(self, floors){
            self.floors = floors;
            self.floors_by_id = {};
            for (var i = 0; i < floors.length; i++) {
                floors[i].tables = [];
                self.floors_by_id[floors[i].id] = floors[i];
            }
            self.floors = self.floors.sort(function(a,b){ return a.sequence - b.sequence; });
            self.config.iface_floorplan = !!self.floors.length;
        },
    });
    models.load_models({
        model: 'restaurant.table',
        fields: ['name','width','height','position_h','position_v','shape','floor_id','color','seats'],
        loaded: function(self,tables){
            self.tables_by_id = {};
            for (var i = 0; i < tables.length; i++) {
                var floor = self.floors_by_id[tables[i].floor_id[0]];
                if (floor) {
                    self.tables_by_id[tables[i].id] = tables[i];
                    floor.tables.push(tables[i]);
                    tables[i].floor = floor;
                }
            }
        },
    });
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            return _super_posmodel.load_server_data.apply(this, arguments).then(function () {
                self.config.iface_floorplan = self.floors.length;
            });
        },
        // analytic datas and merge to current session
        syncing_sessions: function(message) {
            _super_posmodel.syncing_sessions.apply(this, arguments);
            if (message['action'] == 'order_transfer_new_table') {
                this.sync_order_transfer_new_table(message['data']);
            }
            if (message['action'] == 'set_customer_count') {
                this.sync_set_customer_count(message['data']);
            }
            if (message['action'] == 'request_printer') {
                this.sync_request_printer(message['data']);
            }
            if (message['action'] == 'set_note') {
                this.sync_set_note(message['data']);
            }
            this.trigger('update:floor-screen');
        },
        // update new table transfer
        sync_order_transfer_new_table: function (vals) {
            var order = this.get_order_by_uid(vals.uid);
            var current_screen = this.gui.get_current_screen();
            if (order != undefined) {
                if (this.floors_by_id[vals.floor_id] && this.tables_by_id[vals.table_id]) {
                    var table = this.tables_by_id[vals.table_id];
                    var floor = this.floors_by_id[vals.floor_id];
                    if (table && floor) {
                        order.table = table;
                        order.table_id = table.id;
                        order.floor = floor;
                        order.floor_id = floor.id;
                        order.trigger('change', order);
                        if (current_screen) {
                            this.gui.show_screen(current_screen);
                        }
                    }
                    if (!table || !floor) {
                        order.table = null;
                        order.trigger('change', order);
                    }
                }
            }
        },
        sync_order_removing: function (vals) { // if client on this order deleted by other session, will come back to Floor Screen
            var order = this.get_order_by_uid(vals.uid);
            var current_order = this.get_order();
            _super_posmodel.sync_order_removing.apply(this, arguments);
            if (order && current_order&& order.uid == current_order.uid) {
                this.gui.show_screen('floors')
            }
        },
        sync_set_customer_count: function(vals) { // update count guest
            var order = this.get_order_by_uid(vals.uid);
            if (order) {
                order.syncing = true;
                order.set_customer_count(vals.count)
                order.trigger('change', order);
                order.syncing = false;
            }
        },
        sync_request_printer: function(vals) { // update variable set_dirty of line
            var order = this.get_order_by_uid(vals.uid);
            if (order) {
                order.syncing = true;
                order.orderlines.each(function(line){
                    line.set_dirty(false);
                });
                order.saved_resume = order.build_line_resume();
                order.trigger('change', order);
                order.syncing = false;
            }
        },
        // update note of line
        sync_set_note: function(vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.set_note(vals['note']);
                line.syncing = false;
            }
        },

        // return data for floors/tables screen
        get_count_need_print: function(table) {
            var orders = this.get('orders').models;
            var vals = {
                'active_print': 0,
                'unactive_print': 0,
            };
            var orders_current = [];
            for (var x=0; x < orders.length; x ++) {
                if (orders[x].table && orders[x].table.id == table.id) {
                    orders_current.push(orders[x])
                }
            }
            if (orders_current.length) {
                for (i in orders_current) {
                    var order = orders_current[i];
                    for (var i=0; i < order.orderlines.models.length; i ++) {
                        var line = order.orderlines.models[i];
                        if (line.mp_dirty == true) {
                            vals['active_print'] += 1;
                        } else {
                            vals['unactive_print'] += 1
                        }
                    }
                }

            }
            return vals;
        },
    })
})

