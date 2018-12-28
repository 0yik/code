odoo.define('delivery_orders_kds.list_invoice', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var base = require('web_editor.base');

var QWeb = core.qweb;
var Model = require('web.Model');
var PosDB = require("point_of_sale.DB");

var ListInvoiceScreenWidget = screens.ScreenWidget.extend({
    template: 'ListInvoiceScreenWidget',
    model: 'account.invoice',
    previous_screen: 'products',

    init: function(parent, options) {
        this._super(parent, options);
        this.selected_invoices = [];
        var self = this;
        this.search_handler =  function (e) {
            console.log(this.value, e);
            self.load_invoices([['number', 'like', '%'+this.value+'%']]);
        }
    },
    renderElement: function(){
        var self = this
        this._super();
        var order = this.pos.get_order();

        this.el.querySelector('.searchbox input').addEventListener('keyup',this.search_handler);

        this.el.querySelector('.search-clear').addEventListener('click',this.clear_search_handler);

        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
            this.chrome.widget.keyboard.connect($(this.el.querySelector('.searchbox input')));
        }

        if(!order){
            return;
        }
    },

    show: function(){
        var self = this;
        this._super();
        this.renderElement();
        this.$('.back').click(function(){
            if(! self.pos.get_order()){
                var floors = self.pos.floors;
                self.pos.floors_for_temp = floors;
                self.pos.floors = [];
                self.pos.floors_by_id = {};
                for (var i = 0; i < floors.length; i++) {
                    floors[i].tables = [];
                    self.pos.floors_by_id[floors[i].id] = floors[i];
                }
                self.pos.config.iface_floorplan = 0
                self.pos.floors_for_temp = self.pos.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });

                for (var i = self.pos.floors_for_temp.length - 1; i >= 0; i--) {
                    var floor = self.pos.floors_for_temp[i]
                    console.log('TABLES',floor)
                    for (var j = floor.tables.length - 1; j >= 0; j--) {
                        var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                        tables.push([floor.tables[j]['id'],  table_name])
                        console.log('TABLES',floor.tables[j])
                    }
                }
                self.pos.iface_floorplan = 0
                self.pos.add_new_order();
            }
            self.gui.show_popup('deliveryoptionpopup', {
                'title': "LET'S GET STARTED",
            });
        });
        this.$('.next').click(function(){
            self.payment_invoice();
        });
        this.load_invoices([]);
    },
    get_product_by_id: function (product_id) {
        var self = this;
        return new Promise(function (resolve) {
                    var fields = ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
                     'to_weight', 'uom_id', 'description_sale', 'description',
                     'product_tmpl_id','tracking'];
                    new Model('product.product').call('read', [[product_id], fields, base.get_context()]).then(function (data) {
                        if (data.length) {
                            if(!data[0]['uom_id'][0]){
                                data[0]['uom_id'] = [data[0]['uom_id']]
                            }
                            self.pos.db.product_by_id[data[0].id] = data[0];
                            resolve(data[0]);
                        }
                    }).fail(function () {
                        console.log('Cant load delivery product');
                    });
                    });

    },
    payment_invoice: function () {
        var self = this;
        if(self.selected_invoices.length==0){
            alert('Please select invoice!');
            return;
        }
        var table_id = Object.keys(self.pos.tables_by_id)[0];
        var table = self.pos.tables_by_id[table_id];
        //self.pos.table = table;

        self.pos.config.iface_floorplan = 0;
        self.pos.add_new_order();

        self.pos.get_order().table = null;
        var delivery_order = self.pos.get_order();
        var order_invoices = [];
        var product = self.pos.db.get_product_by_id(self.selected_invoices[0].product_id);
        if(! product){
            self.get_product_by_id(self.selected_invoices[0].product_id).then(function (result) {
                product = result;
                self.selected_invoices.forEach(function(line) {
                    var product = self.pos.db.get_product_by_id(line.product_id);
                    if (!product){
                        self.pos.db
                    }
                    if (product) {
                        delivery_order.add_product(product, {
                            quantity: 1,
                            price: line.amount_untaxed,
                        });
                        order_invoices.push(line.id);
                    }

                });
                self.selected_invoices = [];
                delivery_order.order_type = 'delivery';
                delivery_order.order_invoice = order_invoices;
                self.pos.set('selectedOrder', delivery_order);
                self.pos.set_order(delivery_order);
                self.gui.show_screen('payment');
                return;
            });
        }else{
            self.selected_invoices.forEach(function(line) {
                var product = self.pos.db.get_product_by_id(line.product_id);
                if (product) {
                    delivery_order.add_product(product, {
                        quantity: 1,
                        price: line.amount_untaxed,
                    });
                    order_invoices.push(line.id);
                }

            });
            self.selected_invoices = [];
            delivery_order.order_type = 'delivery';
            delivery_order.order_invoice = order_invoices;
            self.pos.set('selectedOrder', delivery_order);
            self.pos.set_order(delivery_order);
            self.gui.show_screen('payment');
        }
    },
    load_invoices: function(domain) {
        var self = this;
        this.selected_invoices = [];
        var invoiceModel = new Model(this.model);
        var branch = this.pos.get_branch();
        if(branch){
            domain.push(['branch_id', '=', branch.id])
        }
        return invoiceModel.call('get_list_invoice', [domain])
            .then(function (invoices) {
                console.log('invoices', invoices);
                self.render_list(invoices);
            }).fail(function (error, event) {
                console.log(error, event);
                event.preventDefault();
            });
    },
    check_invoice: function () {
        return true;
    },
    render_list: function(invoices) {
        var self = this;
        var contents = this.$el[0].querySelector('.invoice-list-contents');
        contents.innerHTML = "";
        for (var i = 0, len = invoices.length; i < len; i++){
            var invoice    = invoices[i];
            console.log('invoice', invoice);
            var invoiceline_html = QWeb.render('InvoiceListLine', {
                widget: this,
                item: invoice
            });

            var invoiceline = document.createElement('tbody');
            invoiceline.innerHTML = invoiceline_html;
            invoiceline = invoiceline.childNodes[1];

            invoiceline.addEventListener('click', function() {
                var element = $(this);
                var invoiceId = this.dataset['id'];
                for (var index = 0, len = invoices.length; index < len; index++) {
                    var item = invoices[index];
                    if (item.id == invoiceId) {
                        if (element.hasClass('highlight')) {
                            element.removeClass('highlight');
                            var select_invoices = [];
                            for (var j = 0, len = self.selected_invoices.length; j < len; j++) {
                                if (self.selected_invoices[j].id != invoiceId) {
                                    select_invoices.push(self.selected_invoices[j]);
                                }
                            }
                            self.selected_invoices = select_invoices;
                        } else {
                            element.addClass('highlight');
                            self.selected_invoices.push(item);
                            // TODO: Create pos
                            console.log('item', item);
                            // self.pos.get('selectedOrder').set_tag(tag);
                        }

                        break;
                    }
                }
            });

            contents.appendChild(invoiceline);
        }
    },
});

gui.define_screen({
    'name': 'invoicelist',
    'widget': ListInvoiceScreenWidget,
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
        var self = this;
        var order = this.pos.get('selectedOrder');
        if ('order_type' in order && order.order_type == 'delivery') {
            var order = self.pos.get_order();
            if(order){
                self.pos.delete_current_order();
            }
        }
        if(! self.pos.get_order()){
            var floors = self.pos.floors;
            self.pos.floors_for_temp = floors;
            self.pos.floors = [];
            self.pos.floors_by_id = {};
            for (var i = 0; i < floors.length; i++) {
                floors[i].tables = [];
                self.pos.floors_by_id[floors[i].id] = floors[i];
            }
            self.pos.config.iface_floorplan = 0
            self.pos.floors_for_temp = self.pos.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });

            for (var i = self.pos.floors_for_temp.length - 1; i >= 0; i--) {
                var floor = self.pos.floors_for_temp[i]
                console.log('TABLES',floor)
                for (var j = floor.tables.length - 1; j >= 0; j--) {
                    var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                    tables.push([floor.tables[j]['id'],  table_name])
                    console.log('TABLES',floor.tables[j])
                }
            }
            self.pos.iface_floorplan = 0
            self.pos.add_new_order();
        }
        return this._super();
    },
});

screens.ActionButtonWidget.include({
    button_click: function(){
        console.log('Inherit action button');
    },
});

var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
             var res = _super_posmodel.prototype.initialize.apply(this, arguments);
             new Promise(function (resolve) {
                 new Model('account.invoice').call('get_delivery_product_id', [[]])
            .then(function (result) {
                if(result && result.product_id){
                    var product = self.db.get_product_by_id(result.product_id);
                    if(!product){
                    var fields = ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
                     'to_weight', 'uom_id', 'description_sale', 'description',
                     'product_tmpl_id','tracking'];
                    new Model('product.product').call('read', [[result.product_id], fields, base.get_context()]).then(function (data) {
                        if (data.length) {
                            if(!data[0]['uom_id'][0]){
                                data[0]['uom_id'] = [data[0]['uom_id']]
                            }
                            product = data[0];
                            self.db.product_by_id[result.product_id] = data[0];
                            resolve(data[0]);
                        }
                    }).fail(function () {
                        console.log('Cant load delivery product');
                    });
                    }
                }
            }).fail(function (error, event) {
                console.log(error, event);
            });

             });

             return res;
        },
    });

var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            Order.add_product.call(this, product, options);
            if(this.pos.category == 'staff_meal') {
                $('.seat_number_from_takeaway').hide();
                $('.btn-newnote').hide();
                $('button.control-button:contains("Transfer")').hide();
                $('button.control-button:contains("Guests")').hide();
                $('button.control-button:contains("Note")').hide();
                $('div.control-button:contains("Rewards")').hide();
            }else if (this.pos.category == 'delivery') {
                $('button.pay').attr("disabled", "disabled");
                $('button.back_delivery_btn').removeClass('oe_hidden');
                $('button.branch_btn').removeClass('oe_hidden');
                $('div.actionpad button.pay').addClass('oe_hidden');
                $('button.order-submit').hide();
                $('button.guest-button').hide();
                $('button.transfer-button').hide();
                $('div.seat_number_from_takeaway').hide();
                $('div.actionpad button.pay').hide();
                $('button.go-back-staff-meal').hide();
            }
        },
    });


screens.OrderWidget.include({
    custom_view_delivery: function(){
        $('button.pay').attr("disabled", "disabled");
        $('button.back_delivery_btn').removeClass('oe_hidden');
        $('button.branch_btn').show();
        $('div.actionpad button.pay').addClass('oe_hidden');
        $('button.order-submit').hide();
        $('button.guest-button').hide();
        $('button.transfer-button').hide();
        $('div.seat_number_from_takeaway').hide();
        $('div.actionpad button.pay').hide();
        $('button.go-back-staff-meal').hide();
    },
    custom_view_staff_meal: function(){
        $('button.pay').removeAttr('disabled');
        $('button.pay').removeAttr('disabled');
        $('.seat_number_from_takeaway').hide();
        $('.btn-newnote').hide();
        $('button.control-button:contains("Transfer")').hide();
        $('button.control-button:contains("Guests")').hide();
        $('button.control-button:contains("Note")').hide();
        $('div.control-button:contains("Rewards")').hide();
        $('.control-button:contains("All Orders")').hide();
        $('button.branch_btn').hide();
        $('button.back_delivery_btn').hide();
    },
    custom_general_view: function(){
        $('button.pay').removeAttr('disabled');
        $('button.pay').removeAttr('disabled');
        $('button.back_delivery_btn').addClass('oe_hidden');
        $('div.actionpad button.pay').removeClass('oe_hidden');
        $('button.order-submit').show();
        $('button.guest-button').show();
        $('button.transfer-button').show();
        $('div.seat_number_from_takeaway').show();
        $('button.pay').show();
        $('button.go-back-staff-meal').show();
        $('button.branch_btn').hide();
    },
    update_summary: function() {
        this._super();
        $('li.orderline .control-button').hide();
        if(this.pos.category == 'staff_meal'){
            this.custom_view_staff_meal();
        }else if (this.pos.category == 'delivery') {
            this.custom_view_delivery();
        }
    }
});

});

