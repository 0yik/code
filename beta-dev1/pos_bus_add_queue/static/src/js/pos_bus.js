odoo.define('pos_bus_add_queue.pos_bus', function (require) {
    "use strict";

    var bus = require('pos_bus_bus');
    var Bus = bus.bus.prototype;
    var session = require('web.session');

    bus.bus = bus.bus.extend({
        initialize: function (pos) {
            Bus.initialize.call(this, pos);
            this.queue_messages = [];
            this.is_sync = true;
            var self= this;
            setInterval(function () {
                self.is_sync = true;
                self.push_message_from_queue();
            }, 5000);
        },
        push_message_to_other_sessions: function (value) {
            let message = {
                user_send_id: this.pos.user.id,
                value: value,
            };
            this.push_message_to_queue(message);
            this.push_message_from_queue();
        },
        push_message_from_queue: function () {
            let self = this;
            if( self.queue_messages.length > 0 && this.is_sync) {
                self.is_sync = false;
                let orders = this.pos.get('orders').models;
                let orders_store = [];
                for (var i = 0; i < orders.length; i++) {
                    orders_store.push(orders[i].export_as_JSON())
                }
                var message = self.queue_messages.shift();
                var sending = function () {
                    console.log("Sending " + message['value']['action'], message);
                    return session.rpc("/longpolling/pos/bus", {
                        message: message,
                        orders_store: orders_store
                    });
                };
                sending().fail(function (error, e) {
                    console.error(error);
                    if (error.message == "XmlHttpRequestError ") {
                        self.pos.db.save_data_false(message);
                        self.is_sync = true;
                        console.log(message['value']['action']);
                    }
                }).done(function () {
                    self.repush_to_another_sessions();
                    setTimeout(function () {
                        self.is_sync = true;
                        self.push_message_from_queue();
                    }, 900);
                })
            }
        },
        push_message_to_queue: function (message) {
            this.queue_messages.push(message);
            this.optimize_queue();
        },
        optimize_queue: function () {
            //optimize action set_quantity
            if(this.queue_messages.length>1){
                for(let i=this.queue_messages.length-1; i>0 ; i-- ){
                    for(let j=i-1; j>=0; j--) {
                        try {
                            if (this.queue_messages[i]['value']['action'] == 'set_quantity'
                                && this.queue_messages[j]['value']['action'] == 'set_quantity'
                                && this.queue_messages[i]['value']['bus_id'] == this.queue_messages[j]['value']['bus_id']
                                && this.queue_messages[i]['value']['data']['uid'] == this.queue_messages[j]['value']['data']['uid']
                            ) {
                                this.queue_messages.splice(j, 1);
                                i--;
                            }
                        }
                        catch (err){
                            console.log(err);
                        }
                    }
                }
            }
            //optimize action sync_next_screen
            if(this.queue_messages.length>1){
                for(let i=this.queue_messages.length-1; i>0 ; i-- ){
                    for(let j=i-1; j>=0; j--) {
                        try {
                            if (this.queue_messages[i]['value']['action'] == 'sync_next_screen'
                                && this.queue_messages[j]['value']['action'] == 'sync_next_screen'
                                && this.queue_messages[i]['value']['bus_id'] == this.queue_messages[j]['value']['bus_id']
                                && JSON.stringify(this.queue_messages[i]['value']['data']) == JSON.stringify(this.queue_messages[j]['value']['data'])
                            ) {
                                this.queue_messages.splice(j, 1);
                                i--;
                            }
                        }
                        catch (err){
                            console.log(err);
                        }
                    }
                }
            }
        },
        get_message_from_other_sessions: function (messages) {
            for (var i = 0; i < messages.length; i++) {
                let message = messages[i];
                if(message[1]['value']){
                    this.pos.syncing_sessions(message[1]['value']);
                }
            }
        },
    });
    return bus.bus;
});
