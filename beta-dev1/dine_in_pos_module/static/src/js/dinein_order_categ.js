odoo.define('dine_in_pos_module.dine_in_pos_module', function (require) {
"use strict";

    var screens = require('point_of_sale.screens');
    var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
    var Model = require('web.DataModel');
    var models = require('point_of_sale.models');
    var Orderline = models.Orderline.prototype;
    var gui = require('point_of_sale.gui');
    var pos_floor = require('pos_restaurant.floors');
    var assign_temp_order_pos = require('assign_temp_order.pos');
    var core = require('web.core');

    var QWeb = core.qweb;

    var Order = models.Order.prototype;



    OptionsPopupWidget.include({
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        events: _.extend({}, OptionsPopupWidget.prototype.events, {
             'click .button.dive_in':  'dive_in_order_category',
        }),
        // dive_in_order_category: function(){
        //     var self = this.pos;
        //     $('.assign-order').removeClass('oe_hidden');
        //     this.pos.category = "dive_in";
        //     self.popup_option = 'Dine In'
        //     // this.pos.category = "dive_in";
        //     this.pos.all_free = false;
        //     this.pos.is_staff_meal = false;
        //     this.pos.dine_is_assign_order = false;
        //     // Fix: To show where it comes from In KDS screen
        //     var def = new $.Deferred();
        //     var fields = _.find(this.pos.models,function(model){
        //         return model.model === 'product.product';
        //     }).fields;
        //     var model = new Model('pos.order.category');
        //     // self.db.product_by_id = {};
        //     self.db.product_by_category_id = {};
        //     $('button.take_away_dinein').removeClass('oe_hidden');
        //     var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
        //     if(this.pos.category == 'dive_in' && $CreateSalesOrderbutton){
        //         $CreateSalesOrderbutton.addClass('oe_hidden');
        //     }
        //     model.call("get_current_category", ['Dine In',fields,this.pos.pricelist.id]).then(function (result) {
        //         if (result != 0){
        //             if (result == 1){
        //                 self.gui.screen_instances['products'].product_list_widget.product_list = [];
        //                 self.db.add_products([]);
        //             }else{
        //                 self.db.add_products(result);
        //                 self.gui.screen_instances['products'].product_list_widget.set_product_list(result);
        //                 self.gui.screen_instances['products'].product_list_widget.renderElement();
        //             }
        //         }else{
        //             alert("Wrong Product Order Category Defined")
        //         }
        //     });
        //     if (!self.config.iface_floorplan ||  self.floors.length == 0 ) {
        //         self.floors = []
        //         // self.floors_by_id = {};
        //
        //         for (var i = 1; i <= Object.keys(self.floors_all_by_id ? self.floors_all_by_id : []).length ; i++) {
        //             if (self.floors_all_by_id[i].id == self.config.floor_ids[0]){
        //                 self.floors.push(self.floors_all_by_id[i])
        //             }
        //
        //             self.floors_by_id[self.floors_all_by_id[i].id] = self.floors_all_by_id[i];
        //         }
        //         if(self.floors && self.floors.length>0 && !self.floors[0].tables.length ){
        //             self.floors[0].tables = []
        //             for(var i=0; i< Object.keys(self.floors[0].table_ids).length ; i++)
        //             {
        //                 self.floors[0].tables.push(self.tables_by_id[ self.floors[0].table_ids[i] ])
        //             }
        //         }
        //         self.config.iface_floorplan = 1;
        //         self.iface_floorplan = 1;
        //         this.gui.set_startup_screen('floors');
        //         this.gui.show_screen('floors');
        //         self.trigger('update:floor-screen');
        //     }
        //     else{
        //         this.gui.show_screen('floors');
        //     }
        // },
    });

    var DineinToTakeawayWidget = screens.ActionButtonWidget.extend({
        template: 'DineinToTakeawayWidget',

        button_click: function() {
            $('button.take_away_dinein').toggleClass('takeaway-apply');
            
            if ($('button.take_away_dinein').hasClass('takeaway-apply')){
                var self = this.pos;
                console.log('In Take Away...',this)
                self.popup_option = 'dive_in_take_away'
                var def = new $.Deferred();
                var fields = _.find(this.pos.models,function(model){ 
                    return model.model === 'product.product'; 
                }).fields;
                var model = new Model('pos.order.category');
                // self.db.product_by_id = {};
                // self.db.product_by_category_id = {};
                model.call("get_current_category", ['Take Away',fields,this.pos.pricelist.id]).then(function (result) {
                    if (result != 0){
                        if (result == 1){
                            self.gui.screen_instances['products'].product_list_widget.product_list = [];
                            self.db.add_products([]);
                        }else{
                            self.db.add_products(result);
                            self.gui.screen_instances['products'].product_list_widget.set_product_list(result);
                            self.gui.screen_instances['products'].product_list_widget.renderElement();
                        }
                    }else{
                        alert("Wrong Product Order Category Defined")
                    }
                });
            }else{
                var self = this.pos;
                console.log('In Dine in...',this)
                self.popup_option = 'Dine In'
                var def = new $.Deferred();
                var fields = _.find(this.pos.models,function(model){ 
                    return model.model === 'product.product'; 
                }).fields;
                var model = new Model('pos.order.category');
                // self.db.product_by_id = {};
                // self.db.product_by_category_id = {};
                model.call("get_current_category", ['Dine In',fields,this.pos.pricelist.id]).then(function (result) {
                    if (result != 0){
                        if (result == 1){
                            self.gui.screen_instances['products'].product_list_widget.product_list = [];
                            self.db.add_products([]);
                        }else{
                            self.db.add_products(result);
                            self.gui.screen_instances['products'].product_list_widget.set_product_list(result);
                            self.gui.screen_instances['products'].product_list_widget.renderElement();
                        }
                    }else{
                        alert("Wrong Product Order Category Defined")
                    }
                });
            }
        },
    });
    screens.define_action_button({
        'name': 'DineintoTakeaway',
        'widget': DineinToTakeawayWidget,
        'condition': function() {
            return true;
        },
    });

    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            this.pos   = options.pos;
            this.popup_option = options.pos.popup_option
            Orderline.initialize.apply(this,arguments);
        },
        export_as_JSON: function() {
            var ret=Orderline.export_as_JSON.call(this);
            ret.popup_option = this.popup_option;
            return ret;
        },
    });

    gui.Gui = gui.Gui.extend({
        show_screen: function(screen_name,params,refresh) {
            var self = this;
            self._super(screen_name,params,refresh);
            if (this.pos.popup_option == 'Dine In' || this.pos.popup_option == 'dive_in_take_away') { 
                $('button.take_away_dinein').removeClass('oe_hidden');
                $('button.take_away_dinein').removeClass('takeaway-apply');
                this.pos.popup_option = 'Dine In';
            }else{
                $('button.take_away_dinein').addClass('oe_hidden');
            }
        }
    });



    models.Order = models.Order.extend({
         initialize: function(attributes,options){
            Order.initialize.apply(this, arguments);            
            this.dine_is_assign_order = false;
        },

        init_from_JSON: function(json) {
            Order.init_from_JSON.call(this, json);
            this.dine_is_assign_order = json.dine_is_assign_order;

        },
        export_as_JSON: function() {
            var ret=Order.export_as_JSON.call(this);
            ret.dine_is_assign_order = this.dine_is_assign_order;
            return ret;
        },
        set_dine_assign_order: function(dine_is_assign_order){
            this.dine_is_assign_order = dine_is_assign_order;
            this.trigger('change',this);
        },
       
    });
    
    assign_temp_order_pos.TempOrdersScreenWidget.include({
        initialize: function(attributes,options){
            this.selected_orders = [];
            this.pos = options.pos;
            this._super(attributes,options);
        },
        events: _.extend({}, assign_temp_order_pos.TempOrdersScreenWidget.prototype.events, {
         'click .process_next_order': 'click_process_next_order',
         'click .temp_orders_back': 'click_back',
        }),
        click_back: function(){
            this.gui.show_screen('products');
        },
        render_list: function(orders, input_txt) {
            this.pos.category = 'dive_in';
            if (this.pos.category == "dive_in"){

                var self = this;
                var contents = $('.temp-order-list-contents');
                contents.html('');
                self.selected_orders = []
                var pos_orders = self.pos.get('orders').models;
                var temp_orders = [];
                for (var i = pos_orders.length - 1; i >= 0; i--) {
                    if(!pos_orders[i].dine_is_assign_order && pos_orders[i].emenu_order){
                        temp_orders.push(pos_orders[i])
                    }
                }


                for (var i = 0, len = temp_orders.length; i < len; i++){
                    var order_id    = temp_orders[i];
                    // var table_seat_no = temp_orders[i].table && temp_orders[i].table.seats or 0;
                    var orderline_html = QWeb.render('tempOrderLine', {
                        widget: this,
                        order: temp_orders[i],
                        index:i,
                        order_date:temp_orders[i].creation_date.getDate()+'/'+(temp_orders[i].creation_date.getMonth()+1)+'/'+temp_orders[i].creation_date.getFullYear(),
                        // table_seat_no:table_seat_no,
                    });
                    var orderline = document.createElement('tbody'); 
                    orderline.innerHTML = orderline_html;
                    orderline = orderline.childNodes[1];

                    orderline.addEventListener('click', function() {
                        var element = $(this);
                        var orderId = this.dataset['id'];
                        var orderuid = this.dataset['uid'];

                        for (var index = 0, len = temp_orders.length; index < len; index++) {
                            var item = temp_orders[index];
                            if (item.uid == orderuid) {
                                if (element.hasClass('highlight')) {
                                    element.removeClass('highlight');
                                    var selected_orders = [];
                                    for (var j = 0, len = self.selected_orders.length; j < len; j++) {
                                        if (self.selected_orders[j].id != orderId) {
                                            selected_orders.push(self.selected_orders[j]);
                                        }
                                    }
                                    self.selected_orders = selected_orders;
                                } else {
                                    element.addClass('highlight'); 
                                    self.selected_orders.push(item);
                                }
                                break;
                            }
                        }

                    });
                    console.log(">>>>>>>>>>orderline ", orderline);
                    contents.append(orderline);
                }
            }
            else{
                this._super(orders, input_txt);
            }
        },
       
        click_process_next_order: function(){
            var self = this;
            var uid = null;
            for (var i = self.selected_orders.length - 1; i >= 0; i--) {
                uid = self.selected_orders[i].uid
                this.pos.get_order_by_uid(self.selected_orders[i].uid).dine_is_assign_order = true;
                this.pos.get_order_by_uid(self.selected_orders[i].uid).table = this.pos.table;
                this.pos.get_order_by_uid(self.selected_orders[i].uid).floors = this.pos.floors;
                this.pos.get_order_by_uid(self.selected_orders[i].uid).save_to_db();
                this.pos.pos_bus.push_message_to_other_sessions({
                        action: 'order_transfer_new_table',
                        data: {
                            uid: self.selected_orders[i].uid,
                            table_id: this.pos.table.id,
                            floor_id: this.pos.table.floor_id[0],
                        },
                        order: this.pos.get_order_by_uid(self.selected_orders[i].uid).export_as_JSON(),
                        bus_id: this.pos.config.bus_id[0],
                    });
            }
            this.pos.set_order( this.pos.get_order_by_uid(uid));
            this.gui.show_screen('products');
        },
    });

    assign_temp_order_pos.AutoAssignOrders.include({
        button_click: function () {
            console.log(">>>>>>>>>>>this.pos ", this.pos);
            if(this.pos.category == 'dive_in'){
                // code for any one order is change into dine_is_assign_order = true;
                var dine_temp_orders = []
                var order = this.pos.get('orders').models;
                var order_created_time = []
                for (var i = order.length - 1; i >= 0; i--) {
                    console.log(">>>>>order[i].dine_is_assign_order ",order[i].dine_is_assign_order, order[i]);
                    if(order[i].dine_is_assign_order == false && order[i].emenu_order){
                        dine_temp_orders.push(order[i]);
                        order_created_time.push(order[i].created_time);
                    }
                }
                if(dine_temp_orders.length == 0){
                    alert('There are no order for assign table');
                }
                for (var i = dine_temp_orders.length - 1; i >= 0; i--) {
                    if (order_created_time.sort()[0] == dine_temp_orders[i].created_time){
                        dine_temp_orders[i].dine_is_assign_order = true;
                        dine_temp_orders[i].table = this.pos.table;
                        this.pos.pos_bus.push_message_to_other_sessions({
                            action: 'order_transfer_new_table',
                            data: {
                                uid: dine_temp_orders[i].uid,
                                table_id: this.pos.table.id,
                                floor_id: this.pos.table.floor_id[0],
                            },
                            order: dine_temp_orders[i].export_as_JSON(),
                            bus_id: this.pos.config.bus_id[0],
                        });
                        dine_temp_orders[i].floors = this.pos.floors;
                        dine_temp_orders[i].save_to_db();
                        alert(dine_temp_orders[i].uid + ' order of '+ dine_temp_orders[i].temp_customer_name +' is auto assigned.');
                        this.pos.set_order( this.pos.get_order_by_uid(dine_temp_orders[i].uid));
                        this.gui.show_screen('products');
                        break;
                    }
                }

                // code for sleected order change into dine_is_assign_order = true
                // if (this.pos.get_order()){
                //     this.pos.get_order().dine_is_assign_order = true;
                // }
            }
            else
            {
                this._super();
            }
        }
    });
    
});
