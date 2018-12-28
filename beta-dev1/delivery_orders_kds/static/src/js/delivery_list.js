odoo.define('delivery_orders_kds.delivery_list', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var models = require('point_of_sale.models');

var QWeb = core.qweb;
var Model = require('web.Model');

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        get_branch: function () {
            try {
                return {
                    id : this.config.branch_id[0],
                    name: this.config.branch_id[1]
                }
            }catch(err) {
                console.log(err);
                return null;
            }
        },
    });
var ListSaleOrderScreenWidget = screens.ScreenWidget.extend({
    template: 'ListSaleOrderScreenWidget',
    model: 'sale.order',
    previous_screen: 'deliveryoptionpopup',

    init: function(parent, options) {
        this._super(parent, options);
        this.selected_orders = [];
        var self = this;
        this.search_handler =  function (e) {
            self.load_sale_orders(['name', 'like', '%'+this.value+'%']);
        }
    },
    renderElement: function(){
        var self = this;
        var linewidget;

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
            self.gui.show_popup('deliveryoptionpopup', {
                'title': "LET'S GET STARTED",
            });
        });
        this.$('.next').click(function(){
            self.validate_delivery();
        });
        this.load_sale_orders();
        this.el.querySelector('.searchbox input').addEventListener('keyup', this.search_handler);
        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
            this.chrome.widget.keyboard.connect($(this.el.querySelector('.searchbox input')));
        }
    },
    validate_delivery: function () {
        var self = this;
        if(self.selected_orders.length==0){
            alert('Please select invoice!');
            return;
        }
        self.gui.show_popup('deliverymanpopup', {
            'title': "Please enter deliver",
            'parent': self,
        });
    },
    validate_delivery_invoice: function (delivery_man) {
        var self = this;
        var order_ids = self.selected_orders.map(function(order) {
                return order.id;
            });
        var orderModel = new Model(this.model);
        orderModel.call('validate_delivery_invoice', [order_ids, delivery_man])
            .then(function (result) {
                self.load_sale_orders();
                self.gui.show_popup('deliveryoptionpopup', {
                    'title': "LET'S GET STARTED",
                });
            }).fail(function (error, event) {
                console.log(error, event);
                self.load_sale_orders();
                event.preventDefault();
            });
    },
    load_sale_orders: function(domain) {
        var self = this;
        console.log("Order list");
        var orderModel = new Model(this.model);
        var branch = this.pos.get_branch();
        var domains = [['is_delivery', '=', false],'|', '&', ['category', '=', 'delivery'], ['invoice_status', '=', 'to invoice'],
                            '&', ['category', '=', 'transfer_out'], ['invoice_status', '=', 'invoiced']];
        var fields = ['id', 'name', 'confirmation_date', 'partner_id', 'user_id', 'amount_total', 'category'];
        if(branch){
            domains.push(['branch_id', '=', branch.id]);
        }
        if(domain){
            domains.push(domain);
        }
        return orderModel.call('search_read', [domains, fields ])
            .then(function (sale_orders) {
                var invoice_status = {
                    'upselling': 'Upselling Opportunity',
                    'invoiced': 'Fully Invoiced',
                    'to invoice': 'To Invoice',
                    'no': 'Nothing to Invoice'
                }
                _.map(sale_orders, function (sale_order) {
                    sale_order.invoice_status = invoice_status[sale_order.invoice_status];
                });
                console.log('sale_orders', sale_orders);
                self.render_list(sale_orders);
            }).fail(function (error, event) {
                console.log(error, event);
                event.preventDefault();
            });
    },
    check_invoice: function () {
        return true;
    },
    render_list: function(sale_orders) {
        var self = this;
        self.selected_orders = [];
        var contents = this.$el[0].querySelector('.saleorder-list-contents');
        contents.innerHTML = "";
        for (var i = 0, len = sale_orders.length; i < len; i++){
            var sale_order    = sale_orders[i];
            var orderline_html = QWeb.render('SaleorderListLine', {
                widget: this,
                item: sale_order
            });
            var orderline = document.createElement('tbody');
            orderline.innerHTML = orderline_html;
            orderline = orderline.childNodes[1];

            orderline.addEventListener('click', function() {
                var element = $(this);
                var order_id = this.dataset['id'];
                for (var index = 0, len = sale_orders.length; index < len; index++) {
                    var item = sale_orders[index];
                    if (item.id == order_id) {
                        if (element.hasClass('highlight')) {
                            element.removeClass('highlight');
                            var selected_orders = [];
                            for (var j = 0, len = self.selected_orders.length; j < len; j++) {
                                if (self.selected_orders[j].id != order_id) {
                                    selected_orders.push(self.selected_orders[j]);
                                }
                            }
                            self.selected_orders = selected_orders;
                        } else {
                            element.addClass('highlight');
                            self.selected_orders.push(item);
                            console.log('item', item);
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
    'name': 'deliverylist',
    'widget': ListSaleOrderScreenWidget,
    'condition': function(){
        return true;
    },
});

screens.PaymentScreenWidget.include({
    validate_order: function(force_validation) {
        var self = this;
        var order = this.pos.get('selectedOrder');
        if ('order_type' in order && order.order_type == 'delivery') {
            var invoiceModel = new Model('account.invoice');
            return invoiceModel.call('validate_delivery_invoice', [order.order_invoice])
                .then(function(result) {
                    var order = self.pos.get_order();
                    if(order){
                        self.pos.delete_current_order();
                    }
                    self.gui.show_popup('optionpopup', {
                        'title': "LET'S GET STARTED",
                    });
                });
        } else {
            return this._super(force_validation);
        }
    },
    click_back: function(){
        var order = this.pos.get('selectedOrder');
        if ('order_type' in order && order.order_type == 'delivery') {
            var order = this.pos.get_order();
            if(order){
                this.pos.delete_current_order();
            }
        }
        if(! this.pos.get_order()){
            this.prepare_order();
        }
        return this._super();
    },
    prepare_order: function () {
        var floors = this.pos.floors;
        this.pos.floors_for_temp = floors;
        this.pos.floors = [];
        this.pos.floors_by_id = {};
        for (var i = 0; i < floors.length; i++) {
            floors[i].tables = [];
            this.pos.floors_by_id[floors[i].id] = floors[i];
        }
        this.pos.config.iface_floorplan = 0
        this.pos.floors_for_temp = this.pos.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });

        for (var i = this.pos.floors_for_temp.length - 1; i >= 0; i--) {
            var floor = this.pos.floors_for_temp[i];
            for (var j = floor.tables.length - 1; j >= 0; j--) {
                var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                tables.push([floor.tables[j]['id'],  table_name]);
            }
        }
        this.pos.iface_floorplan = 0
        this.pos.add_new_order();
    }
});

screens.ActionButtonWidget.include({
    button_click: function(){
        console.log('Inherit action button');
    },
});
});

