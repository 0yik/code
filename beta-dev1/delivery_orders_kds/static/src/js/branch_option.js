odoo.define('delivery_orders_kds.branch_option', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var Model = require('web.DataModel');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var bus = require('pos_bus_bus');
    var session = require('web.session');
    var _t = core._t;
    var bus = require('pos_bus_bus');
    var session = require('web.session');

    models.load_models([{
        model: 'res.branch',
        fields: ['id','name','delivery_charge_id'],
        loaded: function(self, branch) {
            self.db.branch = branch;
            self.db.branches = {};
            _.map(branch, function (br) {
                self.db.branches[br.id] = br;
            })
        },
	}]);

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        show_message_from_other_branchs: function (message) {
            if(this.config.screen_type == "waiter"){
                this.gui.show_popup('branhmessageoptionspopup',{
                    'title': _t("You have transfer out order"),
                    'message': message
                });
            }
        },
        syncing_sessions: function(message) {
            if (message) {
                _super_posmodel.syncing_sessions.apply(this, arguments);
                if (message['action'] == 'transfer_out') {
                    this.show_message_from_other_branchs(message);
                }
            }
        },
        get_branch_id : function () {
            return this.config.branch_id[0];
        }
    });

    bus.bus = bus.bus.extend({
        push_message_to_other_branches: function (value) {
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
                return session.rpc("/longpolling/pos/branches", {
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
        push_message_to_branch: function (value) {
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
                return session.rpc("/longpolling/pos/branch", {
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
                console.log(' Sync DONE ')
            });
        },
    });

    for (var index in gui.Gui.prototype.popup_classes) {
        if(gui.Gui.prototype.popup_classes[index].name=='Create_Sales_Order_popup_widget'){

            var CreateSalesOrderPopupWidget = gui.Gui.prototype.popup_classes[index].widget;
            CreateSalesOrderPopupWidget.include({
                create_sale_order_rpc: function(values) {
                    var self = this;
                    // self.pos.popup_option = 'Delivery'
                    var order = this.pos.get_order();
                    if(self.pos.get_branch_id() == self.pos.get_order().get_receiver_branch_id()) order.saveChanges();
                    (new Model('pos.sales.order')).call('create_pos_sale_order', values)
                    .fail(function(unused, event) {
                        self.gui.show_popup('error', {
                            'title': _t("Error!!!"),
                            'body': _t("Check your internet connection and try again."),
                        });
                    })
                    .done(function(result) {
                        if(JSON.stringify(self.pos.get_branch()) != JSON.stringify(self.pos.get_order().branch)) {
                            self.pos.pos_bus.push_message_to_branch({
                                action: 'transfer_out',
                                uid: self.uid,
                                from_branch_id: self.pos.get_branch_id(),
                                from_branch: self.pos.db.branches[self.pos.get_branch_id()],
                                branch_id: self.pos.get_order().get_receiver_branch_id(),
                                branch: self.pos.db.branches[self.pos.get_order().get_receiver_branch_id()],
                                data: order.export_as_JSON(),
                                bus_id: self.pos.config.bus_id[0],
                                order: order.export_as_JSON(),
                                order_lines: _.map(order.get_orderlines(), function (order_line) {
                                    return order_line.export_as_JSON();
                                })
                            });
                        }
                        self.pos.delete_current_order();
                        self.pos.get_order().branch_id = self.pos.get_branch() && self.pos.get_branch().id;
                        self.gui.show_screen('clientlist');
                        self.gui.show_popup('orderPrintPopupWidget', {
                            'title': result.name,
                            'order_id': result.id
                        });
                    });
                },
            })
        }
    }

    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            Order.initialize.apply(this, arguments);
            if(this.pos.category == 'delivery') {
                this.category = 'delivery';
                this.receiver_branch_id = this.pos.get_branch_id();
            }
        },
        init_from_JSON: function (json) {
            Order.init_from_JSON.apply(this, arguments);
            this.category = json.category ? json.category : this.pos.category;
            this.branch_id = json.branch_id || this.pos.config.branch_id[0];
        },
        set_receiver_branch_id: function(branch_id){
            var branch = this.pos.db.branches[branch_id];
            if(!branch){
                alert('Invalid branch');
                return;
            }
            this.receiver_branch_id = branch_id;
            this.category = this.pos.get_branch_id() == this.receiver_branch_id ? 'delivery' : 'transfer_out';
            this.category == 'transfer_out' ? $('.paymentplan_btn').hide() : $('.paymentplan_btn').show();
        },
        get_branch: function () {
            return this.pos.db.branches[this.branch_id];
        },
        get_receiver_branch_id: function () {
            return this.receiver_branch_id;
        },
        export_as_JSON: function () {
            var res = Order.export_as_JSON.call(this);
            if(this.pos.category == "delivery"){
                res.branch_id = this.receiver_branch_id;
                res.category = this.category;
                res.sender_branch_id = this.pos.get_branch_id();
                res.payment_plan_id = this.get_payment_plan().id;
            }
            return res;
        },
    });

    screens.OrderWidget.include({
        renderElement: function (scrollbottom) {
            this._super(scrollbottom);
            var order = this.pos.get_order();
            if(this.pos.category == 'delivery'){
                $('.paymentplan_btn').show();
                $('.CreateSalesOrderbutton').show();
            }else {
                $('.paymentplan_btn').hide();
                $('.CreateSalesOrderbutton').hide();
            }
            if (order) {
                var branch_id = order.receiver_branch_id;
;
                if (branch_id) {
                    $('button.branch_btn span').text(this.pos.db.branches[branch_id].name);
                }
            }
        },
    })
    var BranchOptionsPopupWidget = PopupWidget.extend({
        template: 'BranchOptionsPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {

        }),
        init: function(parent, options){
            this._super(parent, options);
            this.parent_widget = false;
            this.branch_list = this.pos.db.branch;
        },
        show: function(options){
            options = options || {};
            this._super(options);
            this.parent_widget = options.parent || false;
        },
        click_confirm: function(){
            var branch_id = parseInt($('select.branch_selection').val());
            var branch = this.pos.db.branches[branch_id];
            if(branch){
                this.pos.get_order().set_receiver_branch_id(branch_id);
                $('button.branch_btn span').text(branch.name);
                this.gui.close_popup();
            }
            else{
                alert('Please select a branch');
                return;
            }
        },
    });

    gui.define_popup({name:'branhoptionspopup', widget: BranchOptionsPopupWidget})
    var BranchMessagePopupWidget = PopupWidget.extend({
        template: 'BranchMessagePopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {

        }),
        init: function(parent, options){
            this._super(parent, options);
            this.from_branch = {id: '', name: ''};
            this.order = {id:'', name: ''};
            this.order_lines = [];
        },
        show: function(options){
            options = options || {};
            this.from_branch = options.message.from_branch
            this.order = options.message.order;
            this.order_lines = options.message.order_lines;
            this._super(options);
        },
        click_confirm: function(){
            this.gui.close_popup();
        },
    });

    gui.define_popup({name:'branhmessageoptionspopup', widget: BranchMessagePopupWidget})

    var BranchOptionButton = screens.ActionButtonWidget.extend({
        'template': 'BranchOptionButton',
        get_current_branch: function () {
            return this.pos.get_order() && this.pos.get_order().branch_id ? this.pos.get_order().branch_id : this.pos.config.branch_id[1];
        },
        button_click: function(){
            this.gui.show_popup('branhoptionspopup', {
                'title': _t("SELECT BRANCH"),
            });
        },
    });
    screens.define_action_button({
        'name': 'branch_option',
        'widget': BranchOptionButton,
        'condition': function() {
            return true;
        },
    });


    return BranchOptionsPopupWidget;
});