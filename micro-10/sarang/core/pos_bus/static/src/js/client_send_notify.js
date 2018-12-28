odoo.define('client_send_notify', function (require) {

    var session = require('web.session');
    var core = require('web.core');
    var screens = require('point_of_sale.screens')
    var models = require('point_of_sale.models');
    var bus = require('bus.bus');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            var self = this;
            var res = _super_order.initialize.apply(this, arguments);
            if (!this.created_time) {
                this.created_time = new Date().toLocaleTimeString();
            };
            if (this.pos.pos_bus) {
                this.bind('add', function (order) { // syncing New order
                    if ((self.pos.the_first_load == false || !self.pos.the_first_load) && (order.syncing != true || !order.syncing) && (order.temporary == false || !order.temporary) && self.pos.config.bus_id && self.pos.config.bus_id[0]) {
                        let order = this.export_as_JSON();
                        self.pos.pos_bus.push_message_to_other_sessions({
                            data: order,
                            action: 'new_order',
                            bus_id: self.pos.config.bus_id[0],
                            order: order,
                        });
                    }

                })
                this.bind('remove', function (order) { // syncing remove order
                    if ((order.syncing != true || !order.syncing) && self.pos.config.bus_id && self.pos.config.bus_id[0]) {
                        self.pos.pos_bus.push_message_to_other_sessions({
                            data: {
                                uid: order.uid
                            },
                            action: 'unlink_order',
                            bus_id: self.pos.config.bus_id[0],
                            order: order.export_as_JSON(),
                        });
                    }
                })
                this.orderlines.bind('add', function (line) {
                    if (line.order.temporary == false && (!line.order.syncing || line.order.syncing == false)) {
                        self.pos.pos_bus.push_message_to_other_sessions({
                            data: line.export_as_JSON(),
                            action: 'new_line',
                            bus_id: self.pos.config.bus_id[0],
                            order: line.order.export_as_JSON(),
                        });
                    }
                })
            }
            return res;
        },
        get_session_info: function () {
            return this.session_info;
        },
        set_client: function (client) {
            var res = _super_order.set_client.apply(this, arguments);
            if (!this.syncing || this.syncing == false) {
                if (client) {
                    this.pos.pos_bus.push_message_to_other_sessions({
                        data: {
                            uid: this.uid,
                            partner_id: client.id,
                        },
                        action: 'set_client',
                        bus_id: this.pos.config.bus_id[0],
                        order: this.export_as_JSON(),
                    });
                }
            }
            return res;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.uid = json.uid;
            this.session_info = json.session_info;
            this.created_time = json.created_time;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.session_info = this.session_info;
            json.uid = this.uid;
            json.temporary = this.temporary;
            json.created_time = this.created_time;
            return json;
        },
    });
    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            var res = _super_order_line.initialize.apply(this, arguments);
            if (!this.session_info) {
                this.session_info = {};
                this.session_info['created'] = this.pos.session_info();
            }
            if (!this.uid) {
                var uid = this.order.uid + '-' + this.id;
                this.uid = uid;
            }
            this.order_uid = this.order.uid;
            return res;
        },
        init_from_JSON: function (json) {
            var res = _super_order_line.init_from_JSON.apply(this, arguments);
            this.uid = json.uid;
            this.session_info = json.session_info;
            return res;
        },
        export_as_JSON: function () {
            var json = _super_order_line.export_as_JSON.apply(this, arguments);
            json.uid = this.uid;
            json.session_info = this.session_info;
            json.order_uid = this.order.uid;
            return json;
        },
        set_quantity: function (quantity) {
            var res = _super_order_line.set_quantity.apply(this, arguments);
            if ((!this.syncing || this.syncing == false) && (this.order.syncing == false || !this.order.syncing) && (this.uid && this.order.temporary == false)) {
                let order = this.order.export_as_JSON();
                if (quantity == "") {
                    this.pos.pos_bus.push_message_to_other_sessions({
                        action: 'set_quantity',
                        data: {
                            uid: this.uid,
                            quantity: 0,
                        },
                        bus_id: this.pos.config.bus_id[0],
                        order: order,
                    });
                }
                if (quantity >= 0) {
                    this.pos.pos_bus.push_message_to_other_sessions({
                        action: 'set_quantity',
                        data: {
                            uid: this.uid,
                            quantity: quantity,
                        },
                        bus_id: this.pos.config.bus_id[0],
                        order: order,
                    });
                }
                if (quantity == "remove") {
                    this.pos.pos_bus.push_message_to_other_sessions({
                        action: 'line_removing',
                        data: {
                            uid: this.uid,
                        },
                        bus_id: this.pos.config.bus_id[0],
                        order: order,
                    });
                }
            }
            return res
        },
        set_discount: function (discount) {
            var res = _super_order_line.set_discount.apply(this, arguments);
            if ((!this.syncing || this.syncing == false) && (this.order.syncing == false || !this.order.syncing) && (this.uid && this.order.temporary == false)) {
                let order = this.order.export_as_JSON();
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'set_discount',
                    data: {
                        uid: this.uid,
                        discount: discount,
                    },
                    bus_id: this.pos.config.bus_id[0],
                    order: order,
                });
            }
            return res
        },
        set_unit_price: function (price) {
            var res = _super_order_line.set_unit_price.apply(this, arguments);
            if ((!this.syncing || this.syncing == false) && (this.order.syncing == false || !this.order.syncing) && (this.uid && this.order.temporary == false)) {
                let order = this.order.export_as_JSON();
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'set_unit_price',
                    data: {
                        uid: this.uid,
                        price: price,
                    },
                    bus_id: this.pos.config.bus_id[0],
                    order: order,
                });
            }
            return res
        },
    });
})
