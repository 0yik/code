odoo.define('client_get_notify', function (require) {

    var session = require('web.session');
    var core = require('web.core');
    var screens = require('point_of_sale.screens')
    var models = require('point_of_sale.models');
    var bus = require('bus.bus');
    var exports = require('pos_bus_bus');
    var _t = core._t;
    var Model = require('web.DataModel');

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        session_info: function () {
            var user = this.cashier || this.user;
            return {
                'bus_id': this.config.bus_id[0],
                'user': {
                    'id': user.id,
                    'name': user.name,
                },
                'pos': {
                    'id': this.config.id,
                    'name': this.config.name,
                },
                'date': new Date().toLocaleTimeString(),
            }
        },
        get_session_info: function () {
            var order = this.get_order();
            if (order) {
                return order.get_session_info();
            }
            return null;
        },
        load_server_data: function () {
            var res = _super_posmodel.load_server_data.apply(this, arguments);
            var self = this;
            return res.then(function () {
                if (self.config.bus_id) {
                    self.pos_bus = new exports.bus(self);
                    self.pos_bus.start(); // start syncing between sessions
                }
            }).then(function () {
                if (self.config.bus_id) {
                    self.chrome.loading_message(_t('Waiting restore orders'), 1);
                    return new Model('pos.bus').call('get_cache_order', [self.config.bus_id[0]]).then(function (datas) {
                        if (datas.length > 0) {
                            self.restore_orders(datas);
                        } else {
                            console.log('Have not orders for restore')
                        }

                    });
                }
            })
        },
        restore_orders: function (datas) {
            this.the_first_load = true;
            var orders = [];
            var count = 0;
            for (var i = 0; i < datas.length; i++) {
                var json = datas[i];
                if (this.tables_by_id && this.floors_by_id) {
                    if (json.floor_id && json.table_id && this.floors_by_id[json.floor_id] && this.tables_by_id[json.table_id]) {
                        var ordered = new models.Order({}, {
                            pos: this,
                            json: json,
                        });
                        orders.push(ordered);
                        count += 1;
                    } else {
                        continue;
                    }
                } else {
                    if (json.table_id) {
                        continue;
                    } else {
                        var ordered = new models.Order({}, {
                            pos: this,
                            json: json,
                        });
                        orders.push(ordered);
                        count += 1;
                    }
                }
            }
            console.log('restore order : ' + count)
            orders = orders.sort(function (a, b) {
                return a.sequence_number - b.sequence_number;
            });
            if (orders.length) {
                this.get('orders').add(orders);
            }
            this.the_first_load = false;
        },
        load_orders: function () {
            if (this.config.bus_id) {
                return;
            } else {
                return _super_posmodel.load_orders.apply(this, arguments);
            }
        },
        save_to_db: function () {
            if (this.config.bus_id) {
                return;
            } else {
                return _super_posmodel.load_orders.apply(this, arguments);
            }
        },
        load_new_product_by_id: function (product_id) {
            var self = this;
            var def = new $.Deferred();
            var fields = _.find(this.models, function (model) {
                return model.model === 'product.product';
            }).fields;
            new Model('product.product')
                .query(fields)
                .filter([['id', '=', product_id]])
                .all({'timeout': 3000, 'shadow': true})
                .then(function (products) {
                    self.db.add_products(products[0]);
                }, function (err, event) {
                    event.preventDefault();
                    def.reject();
                });
            return def;
        },
        load_new_partners_by_id: function (partner_id) {

        },
        on_removed_order: function (removed_order, index, reason) { // no need change screen when syncing remove order
            if (removed_order.syncing == true) {
                return;
            } else {
                var res = _super_posmodel.on_removed_order.apply(this, arguments);
            }
        },
        get_order_by_uid: function (uid) {
            var orders = this.get('orders').models;
            var order = orders.find(function (order) {
                return order.uid == uid;
            });
            return order;
        },
        get_line_by_uid: function (uid) {
            var lines = [];
            var orders = this.get('orders').models;
            for (var i = 0; i < orders.length; i++) {
                var order = orders[i];
                for (var j = 0; j < order.orderlines.models.length; j++) {
                    lines.push(order.orderlines.models[j]);
                }
            }
            for (line_index in lines) {
                if (lines[line_index].uid == uid) {
                    return lines[line_index];
                }
            }
        },
        syncing_sessions: function (message) {
            var action = message['action'];
            if (action == 'new_order') {
                this.sync_order_adding(message['data']);
            }
            if (action == 'unlink_order') {
                this.sync_order_removing(message['data']);
            }
            if (action == 'new_line') {
                this.sync_new_line(message['data']);
            }
            if (action == 'set_quantity') {
                this.sync_set_quantity(message['data']);
            }
            if (action == 'line_removing') {
                this.sync_line_removing(message['data']);
            }
            if (action == 'set_discount') {
                this.sync_set_discount(message['data']);
            }
            if (action == 'set_unit_price') {
                this.sync_set_unit_price(message['data']);
            }
            if (action == 'set_client') {
                this.sync_set_client(message['data']);
            }
        },
        sync_order_adding: function (vals) {
            var orders = this.get('orders');
            if (vals.floor_id && vals.table_id) {  // if installed pos_restaurant module of Odoo
                if (this.floors_by_id[vals.floor_id] && this.tables_by_id[vals.table_id]) {
                    var table = this.tables_by_id[vals.table_id];
                    var floor = this.floors_by_id[vals.floor_id];
                    var orders = this.get('orders');
                    if (table && floor) {
                        var order = new models.Order({}, {pos: this, json: vals});
                        this.order_sequence += 1;
                        order.syncing = true;
                        orders.add(order);
                        order.trigger('change', order);
                        order.syncing = false;
                    }
                }
            } else { // not installed pos_restaurant Odoo
                var order = new models.Order({}, {pos: this, json: vals});
                this.order_sequence += 1;
                order.syncing = true;
                orders.add(order);
                order.trigger('change', order);
                order.syncing = false;
                if (orders.length == 1) {
                    this.set('selectedOrder', order);
                }
            }
        },
        sync_order_removing: function (vals) {
            var order = this.get_order_by_uid(vals.uid);
            if (order) {
                order.syncing = true;
                this.db.remove_order(order.id);
                order.destroy({'reason': 'abandon'});
                this.order_sequence -= 1;
            }
        },
        sync_new_line: function (vals) {
            var order = this.get_order_by_uid(vals['order_uid'])
            if (order) {
                order.syncing = true;
                var product = this.db.get_product_by_id(vals['product_id']);
                if (!product) {
                    this.load_new_product_by_id(vals['product_id']);
                    product = this.db.get_product_by_id(vals['product_id']);
                }
                if (product) {
                    order.add_product(product, {
                        price: vals['price_unit'],
                        quantity: vals['qty'],
                    });
                    order.selected_orderline.syncing = true;
                    order.selected_orderline.uid = vals['uid'];
                    order.selected_orderline.session_info = vals['session_info'];
                    order.selected_orderline.trigger('change', order.selected_orderline);
                    order.selected_orderline.syncing = false;
                };
                order.syncing = false;
            }
        },
        sync_line_removing: function (vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.order.orderlines.remove(line);
                line.order.trigger('change', line.order)
                line.syncing = false;
            }
        },
        sync_set_quantity: function (vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.set_quantity(vals['quantity']);
                line.syncing = false;
            }
        },
        sync_set_discount: function (vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.set_discount(vals['discount']);
                line.syncing = false;
            }
        },
        sync_set_unit_price: function (vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.set_unit_price(vals['price']);
                line.syncing = false;
            }
        },
        sync_set_client: function (vals) {
            let partner_id = vals['partner_id'];
            let uid = vals['uid'];
            var client = this.db.get_partner_by_id(partner_id);
            var order = this.get_order_by_uid(uid)
            if (!order) {
                return;
            }
            if (!client) {
                var self = this;
                var fields = _.find(this.models, function (model) {
                    return model.model === 'res.partner';
                }).fields;
                new Model('res.partner')
                    .query(fields)
                    .filter([['id', '=', partner_id]])
                    .all({'timeout': 3000, 'shadow': true})
                    .then(function (partners) {
                        if (partners.length == 1) {
                            self.db.add_partners(partners)
                            order.syncing = true;
                            order.set_client(partners[0])
                            order.trigger('change', order)
                            order.syncing = false;
                        } else {
                            console.log('Loading new partner fail networking')
                        }
                    }, function (err, event) {
                        event.preventDefault();
                    });
            } else {
                order.syncing = true;
                order.set_client(client)
                order.trigger('change', order)
                order.syncing = false;
            }
        },
    });

})
