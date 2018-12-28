odoo.define('pos_cost_price_encryption.price_encryption', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var Widget = require('web.Widget');

    var PosProductWidget = Widget.include({
        priceEncryption: function (price) {
            var self = this;
            const encrypts = {
                "0": self.pos.config.number_0,
                "1": self.pos.config.number_1,
                "2": self.pos.config.number_2,
                "3": self.pos.config.number_3,
                "4": self.pos.config.number_4,
                "5": self.pos.config.number_5,
                "6": self.pos.config.number_6,
                "7": self.pos.config.number_7,
                "8": self.pos.config.number_8,
                "9": self.pos.config.number_9,
                ".": self.pos.config.number_dot,
            };
            price = price.toString();
            var priceEncrypt = '';
            for (var i = 0, len = price.length; i < len; i++) {
                priceEncrypt += encrypts[price[i]];
            }
            return priceEncrypt;
        }
    });
    var Events = Backbone.Events.extend({
        trigger : function(name) {
            if (!this._events) return this;
            var args = slice.call(arguments, 1);
            if (!eventsApi(this, 'trigger', name, args)) return this;
            var events = this._events[name];
            var unipue_events = [];
            if(typeof events === 'object'){
                for(var i=0; i< events.length; i++){
                    var check = true;
                    for(var j=i-1; j>=0; j--){
                        if(events[i].callback.name === events[j].callback.name && events[i].callback.name ==='set_value') check = false;
                    }
                    if(check) unipue_events.push(events[i]);
                }
            }
            else unipue_events = events;

            var allEvents = this._events.all;
            if (events) triggerEvents(unipue_events, args);
            if (allEvents) triggerEvents(allEvents, arguments);
            return this;
        }
    })

});