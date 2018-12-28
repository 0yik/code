odoo.define('pos_report_order_from.pos_order_from', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var db = require('point_of_sale.DB')
var Model = require('web.DataModel');
var PosBus = require('pos_bus_bus');

var PosBusBus = PosBus.bus.prototype;

PosBus.bus = PosBus.bus.extend({
    push_message_to_other_sessions: function (value) {
        let self = this;
        let orders = this.pos.get('orders').models;
        for (var i = 0; i < orders.length; i++) {
            var data = {}
            data.data = orders[i].export_as_JSON()
            data.to_invoice = false
            var posOrderModel = new Model('pos.order');
                posOrderModel.call('create_from_ui',[[data]]).then(function (server_ids) {
            });
            }
            PosBusBus.push_message_to_other_sessions.call(this,value);
        }
    });


var PosModel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
    delete_current_order: function(){
        var order = this.get_order();
        var posOrderModel = new Model('pos.order');
            posOrderModel.call('delete_from_ui',[order.export_as_JSON()]).then(function () {

            });

        PosModel.delete_current_order.call(this);
    }
});

var Order = models.Order.prototype;

models.Order = models.Order.extend({
    export_as_JSON: function() {
        var ret=Order.export_as_JSON.call(this);
        ret.pos_config_2 = this.pos.config.id;
        return ret;
    },
});
var Orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
        this.pos_line_reference = ''
        Orderline.initialize.call(this, attr,options);
        console.log('this.pos_line_reference before   '+this.pos_line_reference)
        if(!this.pos_line_reference){
            this.pos_line_reference = this.order.uid + this.id
        }
        console.log('this.pos_line_reference before   '+this.pos_line_reference)
    },
    init_from_JSON: function(json) {
        Orderline.init_from_JSON.call(this, json);
        this.pos_line_reference = json.pos_line_reference;
    },
    export_as_JSON: function() {
        var ret=Orderline.export_as_JSON.call(this);
        ret.pos_line_reference = this.pos_line_reference;
        console.log('Export as json line '+JSON.stringify(ret))
        return ret;
    }
});
});