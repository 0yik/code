odoo.define('pizzahut_transferout_order.pos_transferout_order', function (require) {
"use strict";
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var DB = require('point_of_sale.DB');

var core = require('web.core');
var _t  = require('web.core')._t;
var session = require('web.session');
var Model = require('web.DataModel');
var utils = require('web.utils');

var bus = require('pos_bus_bus');
var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');

var round_di = utils.round_decimals;
var Orderline = models.Orderline.prototype;
var Order = models.Order.prototype;
var OrderWidget = screens.OrderWidget.prototype;
var round_pr = utils.round_precision;
var QWeb = core.qweb;

// DB.include({
//     remove_order: function(order_id){
//         var orders = this.load('orders',[]);
//         // if(orders && !orders.is_transfer_out){

//         // }
//         alert('baseeeeeeeeeeeeeee  423 423 44444   remove_order 000 ', orders)
//         // orders = _.filter(orders, function(order){
//             // return order.id !== order_id;
//         // });
//         // this.save('orders',orders);
//     },
// });
models.load_models({
    model: 'res.branch',
    fields: [],
    loaded: function(self, branch){
        self.all_branch = branch;
        self.branch_by_id = {};
        for (var i = 0; i < branch.length; i++) {
            self.branch_by_id[branch[i].id] = branch[i];
        }     
    }
});

var TransferOutOptionsPopupWidget = PopupWidget.extend({
    template: 'TransferOutOptionsPopupWidget',
    events: _.extend({}, PopupWidget.prototype.events, {
         'click .button.transfer_out_send_btn': 'click_transfer_out_send',
         'click .button.transfer_out_receive_btn': 'click_transfer_out_receive',
    }),
    click_transfer_out_send: function(){
        var self = this.pos;
        self.category = 'transfer_out';
        self.popup_option = 'Transfer Out'
        var floors = self.floors;
        self.floors_for_temp = floors;
        self.floors = [];
        self.floors_by_id = {};
        for (var i = 0; i < floors.length; i++) {
            floors[i].tables = [];
            self.floors_by_id[floors[i].id] = floors[i];
        }
        self.config.iface_floorplan = 0
        // self.floors_for_temp = self.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });
        for (var i = self.floors_for_temp.length - 1; i >= 0; i--) {
            var floor = self.floors_for_temp[i]
            for (var j = floor.tables.length - 1; j >= 0; j--) {
                var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                tables.push([floor.tables[j]['id'],  table_name])
            }
        }
        this.pos.iface_floorplan = 0

        this.is_transfer_out = true;
        this.pos.add_new_order();
        this.pos.get_order().is_transfer_out = true;
        // if(this.pos.get_order().is_transfer_out){
        $('.destination-button').removeClass('oe_hidden');
        // }
        // else{
        //     $('.destination-button').addClass('oe_hidden');
        // }

        //redirect to product screen
        this.gui.show_screen('products');
        // var self = this.pos;
        var def = new $.Deferred();
        var fields = _.find(this.pos.models,function(model){
            return model.model === 'product.product';
        }).fields;
        var model = new Model('pos.order.category');
        self.db.product_by_id = {};
        self.db.product_by_category_id = {};
        model.call("get_current_category", ['Transfer Out',fields,this.pos.pricelist.id]).then(function (result) {
            console.log('>>>>>Transfer Out>>>>>>>>>>',result)
            if (result != 0){
                if (result == 1){
                    self.gui.screen_instances['products'].product_list_widget.product_list = [];
                    self.gui.screen_instances['products'].product_list_widget.renderElement();
                    self.db.add_products([]);
                }else{
                    self.db.add_products(result);
                    self.gui.screen_instances['products'].product_list_widget.product_list = result;
                    self.gui.screen_instances['products'].product_list_widget.renderElement();
                }
            }else{
                alert("Wrong Product Order Category Defined")
            }
        });
    },
    click_transfer_out_receive : function(){
        var self = this.pos;
        this.gui.show_screen('posorderlist');
    },
});

gui.define_popup({name:'transferoutoptionpopup', widget: TransferOutOptionsPopupWidget});


var OptionsPopupWidget = OptionsPopupWidget.include({
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};
    },
    events: _.extend({}, OptionsPopupWidget.prototype.events, {
         'click .button.transfer_out':  'click_transfer_out',
    }),
    show: function(options){
        options = options || {};
        this._super(options);
        if (this.pos && this.pos.pos_session && this.pos.pos_session.branch_id){
            var orderModel = new Model('pos.order');
            orderModel.call('search_read', [[['destination_branch', '=', this.pos.pos_session.branch_id[0]], ['is_order_proceed', '=', false]]])
                .then(function (result) {
                console.log(">>>>>  $('.red_bot')  >>>>>. result ", result.length, $('.red_bot').length);
                if (result.length){
                    $('.red_bot').removeClass('oe_hidden');
                    return true;
                }
                else{
                    $('.red_dot').addClass('oe_hidden');
                    return false;
                }
            }).fail(function (error, event) {
                  // event.preventDefault();
            });
        }
    },
    click_transfer_out: function(){
        this.gui.show_popup('transferoutoptionpopup', {
            'title': _t("Process"),
        }); 
    },
});


models.Order = models.Order.extend({
    initialize: function(attributes,options){
        Order.initialize.apply(this, arguments); 
        var self = this;
        if(options.json && !options.json.all_branch){
            options.json.all_branch = this.pos.all_branch;
            options.json.branch_by_id = this.pos.branch_by_id;
            this.set_branches(this.pos.all_branch)
        }
    },
    init_from_JSON: function(json) {
        Order.init_from_JSON.call(this, json);
        this.is_transfer_out = json.is_transfer_out;
        this.all_branch = json.all_branch;
        this.transfer_branch_id = json.transfer_branch_id;
        this.transfer_address = json.transfer_address;

    },
    export_as_JSON: function() {
        var ret=Order.export_as_JSON.call(this);
        ret.is_transfer_out = this.is_transfer_out;
        ret.all_branch = this.all_branch;
        ret.transfer_branch_id = this.transfer_branch_id;
        ret.transfer_address = this.transfer_address;
        return ret;
    },
    set_branches: function(all_branch){
        console.log("this.pos ",self.pos);
        this.all_branch = all_branch;
        // this.branch_by_id = branch;
        this.branch_by_id = {};
        for (var i = 0; i < all_branch.length - 1; i++) {
            this.branch_by_id[all_branch[i].id] = all_branch[i];
        }
    }
});


bus.bus = bus.bus.extend({
    push_message_to_other_sessions_branch: function (value) {
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
            return session.rpc("/longpolling/pos/bus/branch", {
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
});



screens.ReceiptScreenWidget.include({
    click_next: function() {
        // this.pos.get_order().finalize();
        this.gui.show_popup('optionpopup', {
            'title': _t("LET'S GET STARTED"),
        });
    },
});    
screens.PaymentScreenWidget.include({
    finalize_validation: function() {
        var self = this;
        var order = this.pos.get_order();
        var result;
        if (order.is_transfer_out){
            if (!order.transfer_branch_id || !order.transfer_address){
                alert("Please select Branch and input address");
            }
            else{
                result =  this._super();
                // send order data in other branch kitchen
                // this.pos.pos_bus.push_message_to_other_sessions_branch({
                //     data: order.export_as_JSON(),
                //     action: 'new_order',
                //     bus_id: this.pos.config.bus_id[0],
                //     order: order.export_as_JSON(),
                // });
            }
        }
        else{
            result =  this._super();
        }
        return result;
    },  
});


var ChooseDestinationBranchPopupWidget = PopupWidget.extend({
    template: 'ChooseDestinationBranch',
    show: function(options){
        options = options || {};
        this._super(options);
        this.renderElement();
    },
    click_confirm: function(){
        var value = this.$('select').val();
        var add = this.$('#transfer_out_address').val();
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,value, add);
        }
    },
});
gui.define_popup({name:'ChooseDestinationBranch', widget:ChooseDestinationBranchPopupWidget});


var DestinationButton = screens.ActionButtonWidget.extend({
    template: 'DestinationButton',
    button_click: function() {
        this.gui.show_popup('ChooseDestinationBranch', {
            'title': 'Transfer out details',
            'branch': this.pos.all_branch,
            'confirm': function(val, add) {
                this.pos.get_order().is_transfer_out = true;
                this.pos.get_order().transfer_branch_id = val;
                this.pos.get_order().transfer_address = add;
            },
        });   
    },
});
screens.define_action_button({
    'name': 'DestinationButton',
    'widget': DestinationButton
});

var PosModel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
    delete_current_order: function(){
        var order = this.get_order();
        if (order && !order.is_transfer_out) {
            PosModel.delete_current_order.apply(this, arguments);
        }
    },
    sync_order_removing: function (vals) {
        // alert('sync_order_removingsync_order_removing')
        var order = this.get_order_by_uid(vals.uid);
        console.log(">>        sync_order_removing       >>>> order.is_transfer_out ", order.is_transfer_out, order)
        if(order && order.is_transfer_out){
            order.destroy({'reason':'abandon'});

        }
        PosModel.sync_order_removing.apply(this, arguments);
    },


});

var ListPOSOrderScreenWidget = screens.ScreenWidget.extend({
    template: 'ListPOSOrderScreenWidget',
    model: 'pos.order',
    previous_screen: '',

    init: function(parent, options) {
        this._super(parent, options);
        this.selected_orders = [];
        this.pos = parent.pos;
    },
    renderElement: function(){
        var self = this
        this._super();
        var order = this.pos.get_order();
        if(!order){
            return;
        }
    },
    show: function(){
        var self = this;
        this._super();
        this.renderElement();
        this.$('.back').click(function(){
            self.gui.show_popup('transferoutoptionpopup', {
                'title': "Process",
            });
        });
        this.$('.next').click(function(){
            
            // self.payment_invoice();
            for (var i=0; i< self.selected_orders.length; i++){
                var orders_data = [];
                var count = 0;
               
                var json = $.parseJSON(self.selected_orders[i].export_as_JSON_data);
                console.log(">>    394 >>json.get('statement_ids') ", json, json.statement_ids);
                if(json.statement_ids){
                    json.statement_ids = []
                }
                    
                console.log(">>>>json.get('statement_ids') ", json.statement_ids);
               
                var ordered = new models.Order({}, {
                    pos: self.pos,
                    json: json,
                });
                orders_data.push(ordered);
                count += 1;

                console.log('restore order : ' + count)
                orders_data = orders_data.sort(function (a, b) {
                    return a.sequence_number - b.sequence_number;
                });
                if (orders_data.length) {
                    self.pos.get('orders').add(orders_data);
                }
                
                var pos_reference = self.selected_orders[i].pos_reference.substr(6,);
                var pos_session_id = self.selected_orders[i].session_id[0];
                var selected_order_id = self.selected_orders[i].id;
                var pos_bus_id = self.selected_orders[i].bus_id[0];
                var orderlines = self.pos.get_order_by_uid(self.selected_orders[i].pos_reference.substr(6,)).orderlines.models;
                for (var i = 0; i < orderlines.length; i++) {
                    orderlines[i].state = 'Confirmed'
                    orderlines[i].next_screen = self.pos.next_screen_by_categ[orderlines[i].product.pos_categ_id[0]]
                }
                self.pos.get_order_by_uid(pos_reference).orderlines.models = orderlines;                
                self.pos.pos_bus.push_message_to_other_sessions_branch({
                    data: self.pos.get_order_by_uid(pos_reference).export_as_JSON(),
                    action: 'new_order',
                    bus_id: pos_bus_id,
                    order: self.pos.get_order_by_uid(pos_reference).export_as_JSON(),
                    select_session: pos_session_id,
                    selected_order_id: selected_order_id,
                });
                self.gui.show_popup('optionpopup', {
                    'title': _t("LET'S GET STARTED"),
                });
            }
        });
        this.load_orders();
    },
    payment_invoice: function () {
        var self = this;
        if(self.selected_invoices.length==0){
            alert('Please select invoice!');
            return;
        }
        var table_id = Object.keys(self.pos.tables_by_id)[0];
        var table = self.pos.tables_by_id[table_id];
        self.pos.table = table;

        self.pos.add_new_order();
        var delivery_order = self.pos.get_order();
        console.log('delivery_order', delivery_order);
        // refund_order.set_client(self.pos.db.get_partner_by_id(order.customer[0]));
        var order_invoices = [];
        self.selected_invoices.forEach(function(line) {
            // delivery_order.set_client(self.pos.db.get_partner_by_id(line.customer.id))
            var product = self.pos.db.get_product_by_id(line.product_id);
            delivery_order.add_product(product, {
                quantity: 1,
                price: line.amount_untaxed,
            });
            order_invoices.push(line.id);
        });
        self.selected_invoices = [];
        delivery_order.order_type = 'delivery';
        delivery_order.order_invoice = order_invoices;
        self.pos.set('selectedOrder', delivery_order);
        self.pos.set_order(delivery_order);
        self.gui.show_screen('payment');
    },
    load_orders: function() {
        var self = this;
        var pos_order = new  Model(this.model);
        return pos_order.call('search_read', [[['destination_branch', '=', this.pos.pos_session.branch_id[0]], ['is_order_proceed', '=', false]]])
                .then(function (result) {
                    self.render_list(result);
                }).fail(function (error, event) {
                      event.preventDefault();
                });
    },
    check_invoice: function () {
        return true;
    },
    render_list: function(orders) {
        var self = this;
        var contents = this.$el[0].querySelector('.invoice-list-contents');
        contents.innerHTML = "";
        for (var i = 0, len = orders.length; i < len; i++){
            var order_id    = orders[i];
            var orderline_html = QWeb.render('posorderListLine', {
                widget: this,
                item: order_id
            });
            var orderline = document.createElement('tbody');
            orderline.innerHTML = orderline_html;
            orderline = orderline.childNodes[1];

            orderline.addEventListener('click', function() {
                var element = $(this);
                var orderId = this.dataset['id'];
                for (var index = 0, len = orders.length; index < len; index++) {
                    var item = orders[index];
                    if (item.id == orderId) {
                        if (element.hasClass('highlight')) {
                            element.removeClass('highlight');
                            var selected_orders = [];
                            for (var j = 0, len = self.selected_orders.length; j < len; j++) {
                                if (self.selected_orders[j].id != orderId) {
                                    selected_orders.push(self.selected_orders[j]);
                                }
                            }
                            console.log("389999  selected_orders 1111 ", self.selected_orders);
                            self.selected_orders = selected_orders;
                            console.log("389999  selected_orders 2222 ", self.selected_orders);
                        } else {
                            element.addClass('highlight');
                            self.selected_orders.push(item);
                        }
                        break;
                    }
                }

            });
            contents.appendChild(orderline);
        }
    },
});
gui.define_screen({
    'name': 'posorderlist',
    'widget': ListPOSOrderScreenWidget,
    'condition': function(){
        return true;
    },
});


return {
    OptionsPopupWidget: OptionsPopupWidget,
    TransferOutOptionsPopupWidget : TransferOutOptionsPopupWidget,
    ListPOSOrderScreenWidget: ListPOSOrderScreenWidget,
}


});
