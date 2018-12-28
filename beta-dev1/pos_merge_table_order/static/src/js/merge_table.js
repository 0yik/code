odoo.define('pos_restaurant.splitbill', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;

var _super_posmodel = models.PosModel.prototype;

var MergeTableScreenWidget = screens.ScreenWidget.extend({
    template: 'MergeTableScreenWidget',
    previous_screen: 'products',

    init: function(parent, options){
        this._super(parent, options);
        var order = this.pos.get_order();
        this.table_list = [];
        this.order = order;
        this.order_total = 0.0;
    },
    renderElement: function(){
        var self = this;
        var linewidget;

        this._super();
        var order = this.pos.get_order();
        if(!order){
            return;
        }
        this.order = order;
        this.order_total = order && order.get_total_with_tax() || 0.0;
        if(order.table) this.addtable(order.table.id);

        if(this.pos.floors.length > 0){
            this.pos.floors.forEach(function (floor) {
                if(floor.id == self.pos.table.floor.id){
                    self.$('#pick-floor').append('<option value="' + floor.id + '" selected>' + floor.name + '</option>');
                }else{
                    self.$('#pick-floor').append('<option value="' + floor.id + '">' + floor.name + '</option>');
                }
            });
        }
        this.renderTableList(self.pos.table && self.pos.table.floor.id);
        this.$('#pick-floor').change(function (e) {
            var floor = $(e.target).val();
            self.renderTableList(floor);
            console.log('Why do you change me?');
        });
        var total_order = 0;
        self.table_list.forEach(function (tableid) {
            var new_order = self.get_table_orders({'id': tableid});
            total_order += new_order.get_total_with_tax();
        });
        this.$('.order-info span.subtotal').text(this.format_currency(total_order));
        this.$('.back').click(function(){
            self.gui.show_screen(self.previous_screen);
        });
    },
    addtable: function (id) {
        if(this.table_list.indexOf(id) == -1 ){
            this.table_list.push(id);
            return true;
        }
        return false;
    },
    removetable: function (id) {
        if(this.table_list.indexOf(id) != -1 && id != this.order.table.id){
            delete this.table_list[this.table_list.indexOf(id)];
            return true;
        }
        return false;
    },
    renderTableList: function (floor) {
        var self=this;
        if(!this.pos.floors_by_id[floor]) return;
        var tables = this.pos.floors_by_id[floor].tables;
        this.$('ul.table-list').html('');
        tables.forEach(function (table) {
            var order = self.get_table_orders(table);
            var data = {
                'id' : table.id,
                'name' : table.name,
                'selected' : table.id && self.table_list.indexOf(table.id) != -1,
                'display_name' : table.floor.name + '(' + table.name + ')',
                'amount_total' : order && order.get_total_with_tax() || 0.0,
            };
            var linewidget = $(QWeb.render('MergeTableline',{
                widget:self,
                table: data,
            }));
            self.$('ul.table-list').append(linewidget);
        })
        this.$('ul.table-list li').click(function(e){
            $(e.target).toggleClass('selected')
            if($(e.target).attr('data-id')){
                var table_id = $(e.target).attr('data-id');
                var order = self.get_table_orders({'id': table_id});
                if(order){
                    if($(e.target).hasClass('selected')){
                        self.addtable(order.table.id) ? self.order_total += order.get_total_with_tax(): null;
                    }else{
                        self.removetable(order.table.id) ? self.order_total -= order.get_total_with_tax(): null;
                    }
                }
            }
            var total_order = 0;
            self.table_list.forEach(function (tableid) {
                var new_order = self.get_table_orders({'id': tableid});
                total_order += new_order.get_total_with_tax();
            });
            self.$('div.order-info .subtotal').text(self.format_currency(total_order));
            console.log('Why do you click me?');
        });
        this.$('.paymentmethods').click(function (e) {
            console.log('Lets payment');
            self.payment();
        })
    },
    get_table_orders: function (table) {
        var orders = this.pos.get("orders").models;
        for (var x=0; x < orders.length; x ++) {
            if (orders[x].table && orders[x].table.id == table.id) {
                return orders[x];
            }
        }
        return null;
    },
    payment: function () {
        var self = this;
        var order = this.pos.get_order();
        order.set('table_list', this.table_list);
        this.table_list.forEach(function (tableid) {
            if(tableid != order.table.id){
                var new_order = self.get_table_orders({'id': tableid});
                var new_orderlines = [];
                for(var i=0; i < new_order.get_orderlines().length; i++){
                    new_orderlines.push(new_order.get_orderlines()[i]);
                }
                for(var i=0; i < new_orderlines.length; i++){
                    order.add_orderline(new_orderlines[i]);
                }
            }
        });
        order.set_screen_data('screen','payment');
        this.gui.show_screen('payment');
    },
    show: function(){
        var self = this;
        this._super();
        this.renderElement();

    },
});

gui.define_screen({
    'name': 'merge_table',
    'widget': MergeTableScreenWidget,
    'condition': function(){
        return true;
    },
});

var MergetTableButton = screens.ActionButtonWidget.extend({
    template: 'MergetTableButton',
    button_click: function(){
        if(this.pos.get_order().get_orderlines().length > 0){
            this.gui.show_screen('merge_table');
        }
    },
});

screens.define_action_button({
    'name': 'merge_table',
    'widget': MergetTableButton,
    'condition': function(){
        return true;
    },
});

});

