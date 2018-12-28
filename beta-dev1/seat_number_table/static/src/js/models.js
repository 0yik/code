odoo.define('seat_number_table.models', function (require) {
"use strict";

var core = require('web.core');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var _super_orderline = models.Orderline.prototype;
var _t = core._t;

models.Orderline = models.Orderline.extend({
   initialize: function(attr, options){
       _super_orderline.initialize.call(this,attr,options);
       this.seat_number = 0;
   },
   init_from_JSON: function(json){
      _super_orderline.init_from_JSON.call(this, json);
      this.seat_number = json.seat_number || 0;
   },
   export_for_printing: function(){
      var json = _super_orderline.export_for_printing.call(this);
      json.seat_number = this.get_seat_number_count() || 0;
      return json;
   },
   get_seat_number_count: function(){
      return this.seat_number || this.pos.get_order().seat_number || 0;
   },
   set_seat_number_count: function(count) {
      this.seat_number = Math.max(count,0);
      this.trigger('change');
   },
   merge: function(orderline){
        this.order.assert_editable();
        if (this.pos.get_order().get_last_orderline() && this.pos.get_order().get_last_orderline().seat_number !== this.pos.get_order().get_seat_number_count()){
            this.pos.get_order().orderlines.add(orderline);
            }
        else{
            this.set_quantity(this.get_quantity() + orderline.get_quantity());
        }
   },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function() {
       _super_order.initialize.apply(this,arguments);
       this.seat_number = 0;
    },
   export_as_JSON: function() {
       var json = _super_order.export_as_JSON.apply(this,arguments);
       json.seat_number = this.get_seat_number_count() || 0;
       return json;
   },
   init_from_JSON: function(json) {
       _super_order.init_from_JSON.apply(this,arguments);
       this.seat_number = json.seat_number || 0;
   },
   export_for_printing: function() {
       var json = _super_order.export_for_printing.apply(this,arguments);
       json.seat_number = this.get_seat_number_count() || 0;
       return json;
   },
   get_seat_number_count: function(){
       return this.seat_number;
   },
   set_seat_number_count: function(count) {
       this.seat_number = Math.max(count,0);
       this.trigger('change');
   },
   add_orderline: function(line){
   this.assert_editable();
   if(line.order){
       line.order.remove_orderline(line);
   }
   line.order = this;
   this.orderlines.add(line);
   this.select_orderline(this.get_last_orderline());
},
get_orderline: function(id){
   var orderlines = this.orderlines.models;
   for(var i = 0; i < orderlines.length; i++){
       if(orderlines[i].id === id){
           return orderlines[i];
       }
   }
   return null;
},

add_product: function(product, options){
    _super_order.add_product.apply(this,arguments);
    var seat_number = this.get_seat_number_count();
    var selected_order_line = this.get_selected_orderline();
    selected_order_line.seat_number = seat_number;
    selected_order_line.trigger('change', selected_order_line);
},
});

var TableSeatNumbersButton = screens.ActionButtonWidget.extend({
   template: 'TableSeatNumbersButton',
   seatnumber: function() {
       if (this.pos.get_order()) {
           return this.pos.get_order().seat_number || 0;
       } else {
           return 0;
       }
   },
   button_click: function() {
       var self = this;
       if (this.pos.get_order().get_selected_orderline()){
           var seat_number = this.pos.get_order().get_selected_orderline().seat_number;
       } else{
           var seat_number = this.pos.get_order().seat_number;
       }
       this.gui.show_popup('number', {
           'title':  _t('Number of Seats ?'),
           'cheap': true,
           'value':  seat_number,
           'confirm': function(value) {
               self.pos.get_order().set_seat_number_count(value);
               self.renderElement();
           },
       });
   },
});

screens.OrderWidget.include({
   update_summary: function(){
       this._super();
       if (this.getParent().action_buttons &&
           this.getParent().action_buttons.seatnumber) {
           this.getParent().action_buttons.seatnumber.renderElement();
       }
   },
});

screens.define_action_button({
   'name': 'seatnumber',
   'widget': TableSeatNumbersButton,
   'condition': function(){
       return this.pos.config.iface_floorplan;
   },
});

return {
   TableSeatNumbersButton: TableSeatNumbersButton,
};

});

