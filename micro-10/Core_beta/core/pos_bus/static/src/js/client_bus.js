odoo.define('pos_bus_bus', function (require) {
    var exports = {}
    var session = require('web.session');
    var Backbone = window.Backbone;
    var core = require('web.core');
    var screens = require('point_of_sale.screens')
    var models = require('point_of_sale.models');
    var bus = require('bus.bus');
    var session = require('web.session');

    exports.bus = Backbone.Model.extend({
        initialize: function (pos) {
            var self = this;
            this.pos = pos;
            this.stop = false;
            setInterval(function () {
                self.repush_to_another_sessions();
            }, 5000);
        },

        push_message_to_other_sessions: function (value) {
            let self = this;
            let orders = this.pos.get('orders').models;
            let orders_store = []
            for (var i = 0; i < orders.length; i++) {
                orders_store.push(orders[i].export_as_JSON())
            }
            let message = {
                user_send_id: this.pos.user.id,
                value: value,
            };
            var sending = function () {
                return session.rpc("/longpolling/pos/bus", {
                    message: message,
                    orders_store: orders_store
                });
            };
            sending().fail(function (error, e) {
                console.error(error);
                if (error.message == "XmlHttpRequestError ") {
                    self.pos.db.save_data_false(message);
                    console.log(' Sync False ')
                }
            }).done(function () {
                self.repush_to_another_sessions();
                console.log(' Sync DONE ')
            })

        },

        get_message_from_other_sessions: function (messages) {
            for (var i = 0; i < messages.length; i++) {
                let message = messages[i];
                this.pos.syncing_sessions(message[1]['value']);
            }
        },

        start: function () {
            this.bus = bus.bus;
            this.bus.last = this.pos.db.load('bus_last', 0);
            this.bus.on("notification", this, this.get_message_from_other_sessions);
            this.bus.start_polling();
        },
        notify: function () {
            $.notify({
                icon: 'pe-7s-gift',
                message: 'Internet or server down, re-sync later',

            }, {
                timer: 500,
                placement: {
                    from: 'top',
                    align: 'right'
                }
            });
        },
        repush_to_another_sessions: function () {
            console.log(' Automatic checking internet and Syncing when connection lost')
            var self = this;
            var datas_false = this.pos.db.get_datas_false();
            if (datas_false) {
                for (var i = 0; i < datas_false.length; i++) {
                    var sending = function () {
                        return session.rpc("/longpolling/pos/bus", {
                            message: datas_false[i],
                            orders_store: {}
                        });
                    };
                    sending().fail(function (error, e) {
                        console.log('===> No internet <===');
                        self.notify()
                    }).done(function (sequence) {
                        self.pos.db.remove_datas_false(sequence);
                    })
                }
            }
        },


    });
    return exports;
})
