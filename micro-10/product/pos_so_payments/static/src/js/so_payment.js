odoo.define('pos_so_payments.so_payment', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var models = require('point_of_sale.models');

var QWeb = core.qweb;
var Model = require('web.Model');

var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.so_invoice = {};
            return _super_posmodel.prototype.initialize.apply(this, arguments);
        },
        set_so_invoice: function (so_invoice) {
            this.so_invoice = so_invoice || {};
        },
        get_so_invoice: function (so_invoice) {
            return this.so_invoice;
        },
        get_so_invoice_total: function () {
            return this.so_invoice.amount_total;
        },
    });

var ListSaleOrderScreenWidget = screens.ScreenWidget.extend({
    template: 'ListSaleOrderScreenWidget',
    model: 'sale.order',
    previous_screen: 'products',

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
            self.gui.show_screen('products');
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
    is_valid_selected_order: function () {
      for(var i =1; i< this.selected_orders.length; i++) {
          if (this.selected_orders[i].partner_id[0] != this.selected_orders[i - 1].partner_id[0]) {
              return false;
          }
      }
      return true;
    },
    validate_delivery_invoice: function (delivery_man) {
        if(!this.is_valid_selected_order){
            alert("Please select orders with the same customer");
            return;
        }
        var self = this;
        var order_ids = self.selected_orders.map(function(order) {
                return order.id;
            });
        var orderModel = new Model(this.model);
        orderModel.call('validate_delivery_invoice', [order_ids, delivery_man])
            .then(function (result) {
                var so_invoice = {
                    'invoice_list': result,
                    'amount_total': _.reduce(_.map(result, function(invoice){ return invoice.amount_total; }), function(memo, num){ return memo + num; }, 0),
                    'invoice_ids': _.map(result, function(invoice){ return invoice.id; }),
                }
                self.pos.set_so_invoice(so_invoice);
                self.gui.show_screen('payment_so');
                self.load_sale_orders();
                // self.gui.show_screen('products');
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
        var domains = [['is_delivery', '=', false],['invoice_status', '=', 'to invoice']];
        var fields = ['id', 'name', 'confirmation_date', 'partner_id', 'user_id', 'amount_total'];
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
    render_list: function(sale_orders) {
        let self = this;
        self.selected_orders = [];
        let contents = this.$el[0].querySelector('.saleorder-list-contents');
        contents.innerHTML = "";
        for (let i = 0, len = sale_orders.length; i < len; i++){
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
    'name': 'list_so_screen',
    'widget': ListSaleOrderScreenWidget,
    'condition': function(){
        return true;
    },
});

});

