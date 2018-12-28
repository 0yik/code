odoo.define('pos_rental.pos_rental', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var time = require('web.time');
var utils = require('web.utils');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');
var PosDB = require('point_of_sale.DB');

var SuperPosModel = models.PosModel.prototype;
var QWeb = core.qweb;
var _t = core._t;
var round_di = utils.round_decimals;

models.load_models({
    model: 'res.partner.category',
    fields: ['display_name'],
    loaded: function(self, partner_tags){
        self.db.partner_tags = partner_tags;
    },
});

models.load_fields('res.partner', ['category_id', 'nric_no'])
models.load_fields('product.product', ['advance_deposit', 'is_booking_product', 'laundry_buffer', 'price', 'qty_available', 'type', 'rent_price']);

// to extend search base on nric no
PosDB.include({
    _partner_search_string: function(partner){
        var str = this._super(partner);
        if(partner.nric_no) {
            str = str.split('\n');
            str += '|' + partner.nric_no + '\n';
        }
        return str;
    }
});

// restrict order quantiy of rented product
screens.OrderWidget.include({
    set_value: function(val) {
        var order = this.pos.get_order();
        var mode = this.numpad_state.get('mode');
        var order_line = order.get_selected_orderline();

        if (mode === 'quantity' && !val) {
            val = 'remove';
        }

        if(mode === 'quantity' && order_line && order_line.product.is_booking_product
            && val !== 'remove' && parseFloat(val) != 1){
            this.numpad_state.resetValue();
            this.gui.show_popup('error', {
                'title': _t('Error'),
                'body': _t('Order quantity of this product is limited to 1.')
            });
        } else {
            return this._super(val);
        }
    }
});

// return product popup
var ProductReturnPopupWidget = PopupWidget.extend({
    template: 'ProductReturnPopupWidget',

    show: function(options){
        var title = '';
        var confirm_btn_str = '';
        if (options.orig_action == 'returned') {
            title  = 'Return Products';
            confirm_btn_str = 'Return';
        } else if (options.orig_action == 'laundry') {
            title = 'Laundry Products';
            confirm_btn_str = 'Laundry';
        } else if (options.orig_action == 'available') {
            title = 'Available Products';
            confirm_btn_str = 'Available';
        }
        this.title = title;
        this.options = options;
        this.confirm_btn_str = confirm_btn_str;
        var self = this;
        var order_id = parseInt(options.order_id);
        var order_line_data = self.pos.db.pos_all_order_lines;
        var actual_lines = _.filter(order_line_data, function(line) {
            return line.order_id[0] == order_id && line.is_booked == true;
        });
        var lines_data = [];
        _.each(actual_lines, function(aline){
            var prd = self.pos.db.get_product_by_id(aline.product_id[0]);
            lines_data.push({'id': prd.id, 'name': prd.display_name, 'barcode': prd.barcode, 'scanned': false});
        });
        options.lines = lines_data;
        this._super(options);

        var barcode_product_action = function(code){
            if (code) {
                var prd = self.pos.db.get_product_by_barcode(code.code);
                if (prd) {
                    product_scan_validate(prd);
                } else {
                    alert('No product found...');
                }
            }
        };

        if (this.pos.barcode_reader) {
            this.pos.barcode_reader.set_action_callback({
                'product': _.bind(barcode_product_action, self)
            });
        };

        var clear_input = function() {
            $('input[name="prod_name"]').val('');
        }

        this.$('input[name="prod_name"]').keypress(function (evt) {
            if (evt.which == 13 && this.value) {
                barcode_product_action({'code': this.value});
                clear_input();
            }
        });

        this.$('.clear').click(function () {
            clear_input();
        });

        var product_scan_validate = function (prod) {
            var input_value = $('input[name="prod_name"]').val();
            var idx = false;
            var l = _.filter(lines_data, function(data, i) {
                if(data.id == prod.id) {
                    idx = i;
                    return true;
                }
            });
            if(l.length > 0) {
                l = l[0];
                if(l.scanned) {
                    alert('Already Scanned...');
                } else {
                    l.scanned = true;
                    $('td[id="'+ l.id +'"]')[0].innerHTML = "<span class='fa fa-check'/>";
                }
            } else {
                alert('Product not found in order...');
            }
        };

        this.$('.confirm').click(function(event) {
            event.preventDefault();
            event.stopPropagation();
            var all_scanned = _.map(lines_data, function(l) { return l.scanned });
            if(all_scanned && _.all(all_scanned)) {
                var orig_this = self.options.orig_this;
                var orig_self = self.options.orig_self;
                var orig_action = self.options.orig_action;
                if (self.options.confirm) {
                    self.options.confirm.call(orig_self, orig_this.id, orig_action, orig_this);
                }
            } else {
                alert('Some items are missing...');
            }
        });
    },

});

gui.define_popup({name:'return-product-screen', widget: ProductReturnPopupWidget});


// advance return popup
var AdvanceReturnPopupWidget = PopupWidget.extend({
    template:'AdvanceReturnPopupWidget',

    show: function(options){
        var self = this;
        var order_id = parseInt(options.order_id);
        var amount = options.amount;
        var obj = options.obj;
        this._super(options);

        self.$(".wk_input").val(amount);
        self.$(".wk_input").focus();

        this.$('.wk_return_confirm').click(function(){
            var price = $(".wk_input").val();

            if (!price) {
                self.pos.gui.show_popup('error',{
                    'title': _("Please define a return amount"),
                });
            } else {
                var order_list = self.pos.db.pos_all_orders;
                var flag = false;
                var message = '';
                var allow_return = true;

                var order = _.filter(order_list, function(order) { return order.id == order_id;});
                order = order && order[0] || undefined;
                if (order && order['return_status'] != '-') {
                    flag = true;
                    message = "Sorry, You can't return some order twice !!"
                    allow_return = false;
                }

                if (allow_return) {
                    if (flag) {
                        self.pos.gui.show_popup('confirm', {
                            'title': _t('Warning !!!'),
                            'body': _t(message),
                            confirm: function() {
                                order.return_status = 'Partially-Returned';
                                self.pos.gui.show_screen(self.previous_screen);
                            },
                        });
                    } else {
                        order.return_status = 'Fully-Returned';
                        new Model('pos.order').call('create_return_advance_payment', [[order_id]], {'price': round_di(price || 0, self.pos.dp['Product Price'])})
                            .then(function (result) {
                                if (result) {
                                    self.pos.gui.show_popup('alert', {
                                        'title': _t('Success !!!'),
                                        'body': _t("Operation Processed Successfully.")
                                    });
                                }
                                $(obj).attr('style','background-color:#e2e2e2 !important');;
                                $(obj).closest('tr').find('.return_status')[0].innerHTML = "<i class='fa fa-check'></i>";
                            })
                    }
                } else {
                    self.pos.gui.show_popup('error', {
                        'title': _t('Not Allowed !!!'),
                        'body': _t(message)
                    });
                }
            }
        });
    }
});

gui.define_popup({name:'return-amount-screen', widget: AdvanceReturnPopupWidget});


// show customer tags
screens.ClientListScreenWidget.include({

    line_select: function(event, $line, id) {
        var self = this;
        var partner = this.pos.db.get_partner_by_id(id);
        var tags = _.filter(self.pos.db.partner_tags, function(tag) {
            return partner.category_id.includes(tag.id);
        });
        var partner_tags = tags.map(function(tag) {
            return {'label': tag.display_name};
        })
        if( (partner_tags.length) > 0) {
            self.pos.gui.show_popup('selection', {
                'title':  _t('Taste or Style'),
                list: partner_tags,
                confirm: function(user){ },
                cancel:  function(){  },
          });
        }
        this._super(event, $line, id);

        // check partner email
        if (!partner.email) {
            alert('There is no email address for sending invoice');
        }
    },
});


// to add deposite product to order
var DepositOrderButton = screens.ActionButtonWidget.extend({
    template: 'DepositOrderButton',

    button_click: function() {
        var self = this;
        var selectedOrder = this.pos.get('selectedOrder');
        if (selectedOrder.orderlines.length > 0 && self.pos.config.advance_product_id) {
            var product = self.pos.db.get_product_by_id(self.pos.config.advance_product_id[0]);
            selectedOrder.add_product(product, {quantity:1, 'check': 'check', price:product.advance_deposit, merge:false});
        }
    },
});

screens.define_action_button({
    'name': 'deposite_product',
    'widget': DepositOrderButton,
});


// screen for today and all orders
var OrderScreenWidget = screens.ScreenWidget.extend({
    template: 'OrderScreenWidget',

    init: function(parent, options){
        this._super(parent, options);
        this.order_cache = new screens.DomCache();
    },

    auto_back: true,

    get_param_show_all: function() {
        return this.gui.get_current_screen_param('show_all');
    },

    get_param_show_today: function() {
        return this.gui.get_current_screen_param('show_today');
    },

    _calculate_order_deposit: function(order_id) {
        var pos = this.chrome.pos;
        var amount = 0;
        var order_line_data = pos.db.pos_all_order_lines;
        var advance_order_lines = _.filter(order_line_data, function(line) {
            return line.order_id[0] == order_id && pos.config.advance_product_id[0] == line.product_id[0]
        });
        amount = _.reduce(advance_order_lines, function(a, b) { return a + b.price_unit; }, 0);
        return amount;
    },
    // to get backend pos orders
    _get_backend_pos_orders: function() {
        return true;
    },

    display_order: function(order_name) {
        var self = this;
        var show_all = this.get_param_show_all();
        var show_today = this.get_param_show_today();
        this._get_backend_pos_orders();
        var order_list = this.pos.db.pos_all_orders;
        // get unpaid orders and not empty pos carts
        var unpaid_orders = _.filter(this.pos.db.get_unpaid_orders(), function(order) { return order.lines.length > 0;});
        if (unpaid_orders.length > 0) {
            order_list = order_list.concat(unpaid_orders);
        }

        if(show_today){
            var filtered_order_list = [];
            for(i=0; i<order_list.length; i++){
                if(order_list[i].date_order){
                    if (moment(show_today).isSame(moment(order_list[i].date_order).format('YYYY-MM-DD'))) {
                        filtered_order_list.push(order_list[i]);
                    }
                }
                // unpaid orders
                else if(order_list[i].creation_date) {
                    if (moment(show_today).isSame(moment(order_list[i].creation_date).format('YYYY-MM-DD'))) {
                        var partner_id = order_list[i].partner_id;
                        var partner = self.pos.db.get_partner_by_id(partner_id);
                        order_list[i].partner_id = [partner_id, partner ? partner.name : '-'];
                        order_list[i].date_order = moment(order_list[i].creation_date).format("YYYY-MM-DD hh:mm:ss");;
                        order_list[i].state = 'draft';
                        order_list[i].id = order_list[i].uid;
                        filtered_order_list.push(order_list[i]);
                    }
                }
            }
            order_list = filtered_order_list;
        }

        if(order_name) {
            var filtered_order_list = [];
            var search_text = order_name.toLowerCase()
            for (i=0; i<order_list.length; i++){
                if (order_list[i].partner_id == '') {
                    order_list[i].partner_id = [0, '-'];
                }
                if (((order_list[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order_list[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1) ||
                    (order_list[i].booking_id.length > 1 && (order_list[i].booking_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                    filtered_order_list.push(order_list[i]);
                }
            }
            order_list = filtered_order_list;
        }

        var contents = this.$el[0].querySelector('.client-list-contents');
        contents.innerHTML = "";
        order_list.sort(function(a,b) {return (a.date_order < b.date_order) ? 1 : ((b.date_order < a.date_order) ? -1 : 0);});

        for(var i=0, len=Math.min(order_list.length,1000); i<len; i++){
            var order = order_list[i];
            var orderline = this.order_cache.get_node(order.id);
            if(!orderline || (orderline && orderline.partner_id != order.partner_id)){
                order.deposit_amount = self._calculate_order_deposit(order.id);
                var orderline_html = QWeb.render('OrderLineBody',{widget: this, order:order});
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                this.order_cache.cache_node(order.id, orderline);
            }
            if(order.partner_id === this.old_client){
                orderline.classList.add('highlight');
            }else{
                orderline.classList.remove('highlight');
            }
            contents.appendChild(orderline);
        }
    },

    show: function(){
        var self = this;
        this._super();

        this.renderElement();
        this.old_client = this.pos.get_order().get_client();

        this.$('.back').click(function(){
            self.gui.back();
        });
        this.$('.order_search').keyup(function() {
            self.display_order(this.value);
        });
        this.display_order();

        this.$('.wk_order_state').click(function(options){
            var order_id = this.id;
            var order = self.chrome.widget['order_selector'].get_order_by_uid(order_id);
            if (order) {
                self.pos.set_order(order);
                self.pos.gui.show_screen('products');
            }
        });

        this.$('.wk_return_content').click(function(options) {
            var order_list = self.pos.db.pos_all_orders;
            var order_line_data = self.pos.db.pos_all_order_lines;
            var order_id = this.id;
            var message = '';
            var allow_return = true;
            var amount = 0;

            var unpaid_orders = _.filter(self.pos.db.get_unpaid_orders(), function(order) {return order.uid == order_id;});
            if (unpaid_orders.length > 0) {
                self.pos.gui.show_popup('error', {
                    'title': _t('Not Allowed !!!'),
                    'body': _t("Please first pay deposit.")
                });
                return;
            }

            var order = _.filter(order_list, function(order) { return order.id == order_id;});
            if (order && order[0] && order[0]['return_status'] != '-') {
                message = "Sorry, You can't return some order twice !!"
                allow_return = false;
            }

            if (allow_return && order[0].returned) {
                amount = self._calculate_order_deposit(order_id);
                self.pos.gui.show_popup('return-amount-screen', {order_id: this.id, 'amount': amount, 'obj':this});
            } else {
                self.pos.gui.show_popup('error', {
                    'title': _t('Not Allowed !!!'),
                    'body': _t("Cannot return an Advance!!!")
                });
            }
        });

        this.$('.wk_collected').click(function(options) {
            self.perform_operation(this.id, 'collected', this);
        });
        this.$('.wk_returned').click(function(options) {
            var order_id = this.id;
            var index = false;
            _.each(self.pos.db.pos_all_orders, function(order, idx) {
                if (order.id == order_id) {
                    index = idx;
                }
            });
            var order = self.pos.db.pos_all_orders[index];
            if(order && order.collected && !order.returned) {
                var orig_this = this;
                var orig_self = self;
                self.pos.gui.show_popup('return-product-screen', {'order_id': order_id, 'confirm': self.perform_operation, 'orig_this': orig_this, 'orig_self': orig_self, 'orig_action': 'returned'});
            } else {
                if (order) {
                    self.pos.gui.show_popup('error', {
                        'title': _t('Not Allowed !!!'),
                        'body': _t("Cannot perform this operation.")
                    });
                }
            }
        });
        this.$('.wk_laundry').click(function(options) {
            var order_id = this.id;
            var index = false;
            _.each(self.pos.db.pos_all_orders, function(order, idx) {
                if (order.id == order_id) {
                    index = idx;
                }
            });
            var order = self.pos.db.pos_all_orders[index];
            if (order && order.collected && order.returned && !order.laundry) {
                var orig_this = this;
                var orig_self = self;
                self.pos.gui.show_popup('return-product-screen', {'order_id': order_id, 'confirm': self.perform_operation, 'orig_this': orig_this, 'orig_self': orig_self, 'orig_action': 'laundry'});
            } else {
                if (order) {
                    self.pos.gui.show_popup('error', {
                        'title': _t('Not Allowed !!!'),
                        'body': _t('Cannot perform this operation.')
                    });
                }
            }
        });
        this.$('.wk_available').click(function(options) {
            var order_id = this.id;
            var index = false;
            _.each(self.pos.db.pos_all_orders, function(order, idx) {
                if (order.id == order_id) {
                    index = idx;
                }
            });
            var order = self.pos.db.pos_all_orders[index];
            if (order && order.collected && order.returned && order.laundry && !order.all_done) {
                var orig_this = this;
                var orig_self = self;
                self.pos.gui.show_popup('return-product-screen', {'order_id': order_id, 'confirm': self.perform_operation, 'orig_this': orig_this, 'orig_self': orig_self, 'orig_action': 'available'});
            } else {
                if (order) {
                    self.pos.gui.show_popup('error', {
                        'title': _t('Not Allowed !!!'),
                        'body': _t('Cannot perform this operation.')
                    });
                }
            }
        });
        this.$('.view_products').click(function(options) {
            var order_id = this.id;
            var products = [];

            if (order_id.split('-').length > 1) {
                var order = _.filter(self.pos.db.get_unpaid_orders(), function(ord) { return ord.id == order_id});
                if (order.length > 0) {
                    _.each(order[0].lines, function(line) {
                        if (line[2].is_ordered === true) {
                            products.push({'id': line[2].product_id});
                        }
                    });
                }
            } else {
                var prd_ids = _.filter(self.pos.db.pos_all_order_lines, function(line) { return line.order_id[0] == order_id && line.is_ordered === true; })
                    .map(function(ln) { return ln['product_id'][0]; });
                _.each(prd_ids, function(pid) {
                    products.push({'id': pid});
                });
            }
            function get_product_image_url(prd_id) {
                return window.location.origin + '/web/image?model=product.product&field=image_small&id='+prd_id;
            }
            if (products.length > 0) {
                _.each(products, function(prd) {
                    prd['label'] = self.pos.db.get_product_by_id(prd.id).display_name;
                    prd['image_url'] = get_product_image_url(prd.id);
                });
                self.pos.gui.show_popup('selection', {
                    'title': _('Products'),
                    'list': products,
                    'confirm': function(user) {},
                    'cancel': function() {}
                })
            }
        });
    },

    perform_operation: function(order_id, operation, obj) {
        var self = this;
        var do_operation = false;
        var index = false;

        _.each(self.pos.db.pos_all_orders, function(order, idx) {
            if (order.id == order_id) {
                index = idx;
            }
        });
        var order = self.pos.db.pos_all_orders[index];

        if (order) {
            if (operation == 'collected') {
                if (!order.collected) {
                    do_operation = true;
                }
            }
            else if (operation == 'returned') {
                if (order.collected && !order.returned) {
                    do_operation = true;
                }
            }
            else if (operation == 'laundry') {
                if (order.collected && order.returned && !order.laundry) {
                    do_operation = true;
                }
            }
            else if (operation == 'available') {
                if (order.collected && order.returned && order.laundry && !order.all_done) {
                    do_operation = true;
                }
            }
            if (do_operation) {
                (new Model('pos.order')).call('perform_button_operation', [[parseInt(order_id)]], {'operation': operation})
                    .then(function (result) {
                    if (result.error){
                        self.pos.gui.show_popup('error', {
                            'title': _t('Unable to Process !!!'),
                            'body': _t(result.message)
                        });
                    }
                    else{
                        self.pos.gui.show_popup('alert', {
                            'title': _t('Success !!!'),
                            'body': _t("Operation Processed Successfully.")
                        });
                        $(obj).attr('style','background-color:#e2e2e2 !important');

                        if (operation == 'collected'){
                            self.pos.db.pos_all_orders[index].collected = true;
                        }
                        if (operation == 'returned'){
                            self.pos.db.pos_all_orders[index].returned = true;
                        }
                        if (operation == 'laundry'){
                            self.pos.db.pos_all_orders[index].laundry = true;
                        }
                        if (operation == 'available'){
                            self.pos.db.pos_all_orders[index].all_done = true;
                        }
                    }
                });
            } else {
                self.pos.gui.show_popup('error', {
                    'title': _t('Not Allowed !!!'),
                    'body': _t("Cannot perform this operation.")
                });
            }
        } else {
            self.pos.gui.show_popup('error', {
                'title': _t('Not Allowed !!!'),
                'body': _t("Please first pay deposit.")
            });
        }
    },
});

gui.define_screen({name:'order_history', widget: OrderScreenWidget});

var FullOrderHistoryButton = screens.ActionButtonWidget.extend({
    template: 'FullOrderHistoryButton',
    button_click: function(){
        this.pos.gui.show_screen('order_history', {'show_all': true});
    },
});

screens.define_action_button({
    'name': 'full_order',
    'widget': FullOrderHistoryButton,
});

var TodayOrderHistoryButton = screens.ActionButtonWidget.extend({
    template: 'TodayOrderHistoryButton',
    button_click: function(){
        var today_date = moment().format('YYYY-MM-DD');
        this.pos.gui.show_screen('order_history', {'show_today': today_date});
    },
});

screens.define_action_button({
    'name': 'today_order',
    'widget': TodayOrderHistoryButton,
});


var PosOrderSuper = models.Order;
models.Order = models.Order.extend({
	template:'Order',

    initialize: function(attributes, options){
    	var self = this;
    	options = options || {};

    	this.wk_selected_dates = false;
        this.laundry_buffer = 0;
        this.booking_id = false;
        this.booked_lines = {};
        this.return_date = false;
        this.return_status = '-';
        this.is_return_order = false;
        this.return_order_id = false;
        this.old_order_id = false;
        PosOrderSuper.prototype.initialize.apply(this, arguments);
        this.to_invoice = true;

    },
    init_from_JSON: function(json) {
        if (json.booking_id) {
            this.booking_id = json.booking_id;
            this.booked_lines = json.booked_lines;
        }
        PosOrderSuper.prototype.init_from_JSON.apply(this, arguments);
    },
    add_product: function(product, options){
        var self = this;
        var selectedOrder = self.pos.get('selectedOrder');

        if (!selectedOrder.get_client()) {
            alert("Customer not selected.");
            return;
        }

        if (options){
            PosOrderSuper.prototype.add_product.call(this, product, options);
        } else {
            if (product.is_booking_product) {
                var orderLines = selectedOrder.orderlines.models;
                var line_exist = _.filter(orderLines, function(line) { return line.product.id == product.id});
                if (line_exist && line_exist.length > 0) {
                    alert('You cannot book an item twice!!');
                    return;
                }
                if (self.pos.chrome.screens.products.product_categories_widget.mode == 'rent') {
                    self.pos.gui.show_popup('pos-booking-calendar', product);
                } else {
                    if (product.qty_available > 0) {
                        PosOrderSuper.prototype.add_product.call(this, product, options);
                        selectedOrder.get_selected_orderline().is_ordered = true;
                    } else {
                        alert('Product is not available for sale.');
                        return;
                    }
                }
            } else {
                PosOrderSuper.prototype.add_product.call(this, product, options);
            }
        }
    },
    
    export_as_JSON: function() {
        var loaded = PosOrderSuper.prototype.export_as_JSON.apply(this, arguments);

        var current_order =  this.pos.get_order();
        if (current_order) {
	        loaded.is_return_order = current_order.is_return_order;
	        loaded.return_status = current_order.return_status;
	        loaded.return_date = current_order.return_date;
	        loaded.return_order_id = current_order.return_order_id;
        }
        loaded.booked_lines = this.booked_lines;
        loaded.laundry_buffer = this.laundry_buffer;
        loaded.old_order_id = this.old_order_id;
        loaded.booking_id = this.booking_id;

        return loaded;
    },

    remove_orderline: function( line ){
        var is_booked = _.contains(_.keys(this.booked_lines), line.product.id.toString());
        if (is_booked) {
            var fields = {};
            fields['product_id'] = line.product.id;
            fields['booking_id'] = this.booking_id[0];

            // delete booking order line
            new Model('booking.order').call('remove_product_from_booking', [fields]).then(function() {
            });
        }
        PosOrderSuper.prototype.remove_orderline.apply(this, arguments);
    },
});

// switch between mode (sale/rent)
screens.ProductCategoriesWidget.include({
    init: function(parent, options){
        var self = this;
        this._super(parent, options);
        this.mode = 'rent';

        this.change_mode = function(event){
            self.mode = self.mode == 'rent'? 'sale': 'rent';
            this.innerText = 'Mode : ' + self.mode.toUpperCase();
            self.pos.gui.show_popup('alert', {
                'title': "Mode changed",
                'body': 'Now mode is ' + self.mode.toUpperCase()
            });
        };
    },
    renderElement: function(){
        this._super();
        this.el.querySelector('#change_mode').addEventListener('click', this.change_mode);
    }
});


// booking calendar
var PosBookingCalendar = PopupWidget.extend({
    template:'PosBookingCalendar',

    show: function(product, old_order_id){
        this.renderElement();
        this._super();
        var self = this;
        (new Model('product.product')).call('get_product_data', [product], {})
        .then(function (result) {
            $('#calendar').fullCalendar({
                header: {
                    left: 'prev',
                    center: 'title',
                    right: 'next',
                },
                defaultDate: new Date(),
                selectable: true,
                selectHelper: true,

                dayClick: function() {
                    var check = true;
                    var qty = product.qty_available;
                    var selected_date = $(this).attr('data-date');
                    var date = new Date(selected_date);

                    result.forEach(function(r) {
                        if (product.type == 'stockable') {
                            if (r.end){
                                if (r.start<=date && r.end>=date) {
                                    qty = qty - r.product_qty
                                    if (qty < 1) {
                                        check = false;
                                    }
                                }
                            }
                            else{
                                if (_.isEqual(r.start, date)){
                                    qty = qty - r.product_qty
                                    if (qty < 1){
                                        check = false;
                                    }
                                }
                            }
                        }
                    });
                    if (check){
                        var today = new Date().toJSON().slice(0,10);
                        today = new Date(today);
                        if (today-date >0){
                            alert('Booking for past days not allowed!!!');
                        }
                        else {
                            if (qty < 1 && product.type == 'stockable'){
                                alert('Qty available ' + qty);
                            }
                            else{
                                self.update_selected(date);
                                $(this).toggleClass('fc-highlight');
                            }
                        }
                    }
                    else{
                        if (qty < 1) {
                            alert('Qty available ' + qty);
                        }
                    }
                },
                editable: true,
                eventLimit: true,
                events:result,
            });
        });

        this.$('.wk_button_close').off('click').click(function(){
            var selectedOrder = self.pos.get('selectedOrder');
            selectedOrder.wk_selected_dates = false;
            self.gui.close_popup();
        });

        this.$('.wk_button_book').off('click').click(function(){
            var date = $('select.wk_top_title').find('option:selected').attr('value');
            self.validate_dates(product, date);
            var selectedOrder = self.pos.get('selectedOrder');
            selectedOrder.wk_selected_dates = false;
            self.gui.close_popup();
            
        });
    },
    update_selected: function(date) {
        var selectedOrder = this.pos.get('selectedOrder');
        var exists = false;
        if (selectedOrder.wk_selected_dates) {
            if (selectedOrder.wk_selected_dates.length > 0) {
                var selected = selectedOrder.wk_selected_dates;
                selected.forEach(function(d) {
                    if (_.isEqual(d, date)){
                        exists = true;
                        var index = selected.indexOf(d);
                        selected.splice(index, 1);
                    }
                });
                if (!exists) {
                    selected.push(date);
                    selectedOrder.wk_selected_dates = selected;
                }
            } else {
               selectedOrder.wk_selected_dates = [date]; 
            }
        } else {
            selectedOrder.wk_selected_dates = [date];
        }
    },

    add_product_to_booking_order: function(product, days){
        var self = this;
        var fields = {};
        var status = new $.Deferred();
        var selectedOrder = this.pos.get('selectedOrder');
        fields['product_id'] = product['id'];
        fields['buffer_days'] = days;
        fields['dates'] = selectedOrder.wk_selected_dates;
        fields['booking_id'] = selectedOrder.booking_id || false;
        fields['partner_id'] = this.pos.get_order().get_client().id;

        // create booking order
        var status = new Model('booking.order').call('create_from_pos_ui', [fields]).then(function(booking_id) {
            if (booking_id) {
                selectedOrder.booking_id = booking_id.slice(0, 2);
                selectedOrder.start_date = booking_id[2];
                selectedOrder.end_date = booking_id[3];
                return true;
            } else {
                selectedOrder.wk_selected_dates = false;
                // self.gui.close_popup();
                self.gui.show_popup('error', {
                    'title': _t('Error'),
                    'body': _("This product is already booked for selected dates.")
                });
                return false;
            }
        });
        return status;
    },

    _calculate_rent_price: function(days, price) {
        var total_price = 0;
        if (days) {
            // count for weeks and price
            var weeks = parseInt(days / 7);
            days = days % 7;
            if (days > 3) {
                weeks += 1;
                days = 0;
            }
            total_price = price * weeks * 1.5;

            // count for 3-days
            var tdays = parseInt(days / 3);
            days = days % 3;
            total_price += price * tdays;

            // count for 2 day (actually for a day)
            if (days > 1) {
                days = 0;
                total_price += price * 0.75;
            }

            // count for a day (actually for 7 hour)
            if (days) {
                total_price += price * 0.50;
            }
        }
        return parseFloat(parseFloat(total_price).toFixed(2));
    },

    validate_dates: function(product, laundry_buffer) {
        var self = this;
        var selectedOrder = this.pos.get('selectedOrder');
        if (selectedOrder.wk_selected_dates) {
            if (selectedOrder.wk_selected_dates.length>0) {
                var selected = selectedOrder.wk_selected_dates;
                var selected_data = new Array();
                var offset = 0;
                selected.forEach(function(dat) {
                    offset = dat.getTimezoneOffset();
                    var tzDifference = -dat.getTimezoneOffset();
                    dat = new Date(dat.getTime() + tzDifference*60  * 1000);
                    selected_data.push(time.datetime_to_str(dat));
                });
                selected_data.sort();
                var min = selected_data[0];
                var max = selected_data[selected_data.length - 1];
                var min1 = new Date(min);
                var max1 = new Date(max);
                var dd = max1.getDate();
                var mm = max1.getMonth()+1;
                var yyyy = max1.getFullYear();
                var return_date = mm+'/'+dd+'/'+yyyy;

                var diff = (((((max1-min1)/1000)/60)/60)/24) +1;
                if (selectedOrder.wk_selected_dates.length == diff) {
                    self.add_product_to_booking_order(product, laundry_buffer).then(function (val) {
                        if (val) {
                            var price = self._calculate_rent_price(diff, product.rent_price);
                            selectedOrder.booked_lines[product.id] = {'start': min, 'end': max,'product_qty':1, 'laundry_buffer':laundry_buffer}
                            selectedOrder.add_product(product, {quantity:1, 'check': 'check', price:price, merge:false});
                            var line_with_book = selectedOrder.get_selected_orderline();
                            line_with_book.collect_date = min;
                            line_with_book.return_date = max;
                            line_with_book.is_ordered = true;
                            line_with_book.is_booked = true;
                            selectedOrder.return_date = return_date;
                            selectedOrder.selected_orderline.advance_deposit = product.advance_deposit;
                            if (self.pos.config.advance_product_id) {
                                var prod = {'product': self.pos.db.get_product_by_id(self.pos.config.advance_product_id[0])};
                                selectedOrder.add_product(prod, {quantity:1, 'check': 'check', price:0, merge:false});
                            }
                            var line = selectedOrder.selected_orderline;
                            line.set_quantity(1);
                        }
                    })
                } else {
                    alert('You need to select dates in sequence!');
                }
            } else {
               alert('No dates Selected!!!'); 
            }
        } else {
            alert('No dates Selected!!!');
        }
    }
});

gui.define_popup({name:'pos-booking-calendar', widget: PosBookingCalendar});

//kunal chavda

var PosOrderlineSuper = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    template:'Orderline',
    initialize: function(attr,options){
        this.advance_deposit=0.0;
        this.collect_date = false;
        this.return_date = false;
        this.is_booked = false;
        this.is_ordered = false;
        if (options['product']){
            if (options['product']['product']) {
                options['product'] = options['product']['product'];
            }
        } else {
            options['product'] = undefined;
        }
        PosOrderlineSuper.initialize.apply(this, arguments);
    },
    init_from_JSON: function(json) {
        if (json.collect_date && json.return_date) {
            this.collect_date = json.collect_date;
            this.return_date = json.return_date;
            this.is_booked = json.is_booked;
        }
        this.is_ordered = json.is_ordered;
        PosOrderlineSuper.init_from_JSON.apply(this, arguments);
    },
    export_as_JSON: function() {
    	var loaded = PosOrderlineSuper.export_as_JSON.apply(this, arguments);
        loaded.advance_deposit =this.get_product().advance_deposit;
        if (this.collect_date && this.return_date) {
            loaded.collect_date = this.collect_date;
            loaded.return_date = this.return_date;
            loaded.is_booked = this.is_booked;
        }
        loaded.is_ordered = this.is_ordered;
        return loaded;
    },
    set_product_lot: function(product){
        this.has_product_lot = false; // product.tracking !== 'none';
        this.pack_lot_lines  = []; // this.has_product_lot && new PacklotlineCollection(null, {'order_line': this});
    },
    get_booking_str: function() {
        if (this.collect_date && this.return_date) {
            return "On rent from " + this.collect_date.split(' ')[0] + " to " + this.return_date.split(' ')[0];
        }
        return '';
    }
});

models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        SuperPosModel.initialize.call(this, session, attributes);
        var self = this;
        self.models.push(
        {
            model:  'pos.order',
            fields: ['id', 'name', 'date_order', 'partner_id', 'lines', 'pos_reference','is_return_order','return_order_id','return_status', 'return_date', 'order_status', 'returned','collected','laundry','all_done', 'state', 'booking_id', 'start_date', 'end_date', 'invoice_id'],
            domain: function(self){ 
                var domain_list = []
                if (self.config.load_orders_after_this_date) {
                    domain_list = [
                        ['is_return_order', '=', 0],
                        ['date_order', '>', self.config.load_orders_from],
                        ['state', 'not in', ['cancel']]
                    ]
                } else {
                    domain_list = [
                        ['is_return_order', '=', 0],
                        ['session_id', '=', self.pos_session.name],
                        ['state', 'not in', ['cancel']]
                    ]
                }
                return domain_list;
            },
            loaded: function(self, orders){ 
                self.db.pos_all_orders = orders;
            }
        },
        {
            model:  'pos.order.line',
            fields: ['create_date','discount','display_name','id','order_id','price_subtotal','price_subtotal_incl','price_unit','product_id','qty','write_date','is_booked', 'is_ordered'],
            domain: function(self) {
                var order_lines = []
                var orders = self.db.pos_all_orders;
                for (var i = 0; i < orders.length; i++) {
                    order_lines = order_lines.concat(orders[i]['lines']);
                }
                return [
                    ['id', 'in', order_lines]
                ];
            },
            loaded: function(self, wk_order_lines) {
                self.db.pos_all_order_lines = wk_order_lines;
            },
        });
    },

    push_and_invoice_order: function(order){
        var self = this;
        var invoiced = new $.Deferred(); 

        if(!order.get_client()){
            invoiced.reject('error-no-client');
            return invoiced;
        }

        var order_id = this.db.add_order(order.export_as_JSON());

        this.flush_mutex.exec(function(){
            var done = new $.Deferred(); // holds the mutex
            var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});   
            transfer.fail(function(){
                invoiced.reject('error-transfer');
                done.reject();
            });
            transfer.pipe(function(order_server_id){    
                self.chrome.do_action('point_of_sale.pos_invoice_report',{additional_context:{
                    active_ids:[order_server_id[0]],
                }});

                invoiced.resolve();
                done.resolve();
            });
            return done;
        });
        return invoiced;
    },

    _save_to_server: function (orders, options) {
        if (!orders || !orders.length) {
            var result = $.Deferred();
            result.resolve([]);
            return result;
        }

        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;

        var posOrderModel = new Model('pos.order');
        return posOrderModel.call('create_from_ui',
            [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                order.data.booking_id = order.data.booking_id && order.data.booking_id[0] || undefined;
                return order;
            })],
            undefined,
            {
                shadow: !options.to_invoice,
                timeout: timeout
            }
        ).then(function (server_ids) {
            _.each(orders, function (order) {
                self.db.remove_order(order.id);
            });

            posOrderModel.query(['id', 'name', 'date_order', 'partner_id', 'lines', 'pos_reference','is_return_order','return_order_id','return_status', 'return_date', 'order_status', 'returned','collected','laundry','all_done', 'state', 'booking_id', 'start_date', 'end_date', 'invoice_id', 'mail_status'])
                .filter([['id', 'in', server_ids]])
                .all()
                .then(function (ords) {
                    _.each(ords, function(ord) {
                        self.db.pos_all_orders.unshift(ord);
                        var body_msg = ''
                        if (ord.mail_status && ord.mail_status == 'sent' || ord.mail_status == 'received') {
                            body_msg = 'Mail sent successfully'
                        } else {
                            body_msg = 'Mail not sent successfully'
                        }
                        self.gui.show_popup('alert', {
                            'title': _t('Status'),
                            'body': _t(body_msg)
                        });
                    });
                });
            new Model('pos.order.line').query(['create_date','discount','display_name','id','order_id','price_subtotal','price_subtotal_incl','price_unit','product_id','qty','write_date','is_booked', 'is_ordered'])
                .filter([['order_id', 'in', server_ids]])
                .all()
                .then(function (lines) {
                    _.each(lines, function(line) {
                        self.db.pos_all_order_lines.unshift(line);
                    });
                });
            return server_ids;
        }).fail(function (error, event){
            if(error.code === 200 ){    // Business Logic Error, not a connection problem
                self.gui.show_popup('error', {
                    message: error.data.message,
                    comment: error.data.debug
                });
            }
            event.preventDefault();
            console.error('Failed to send orders:', orders);
        });
    },
    });

    return {
        'OrderScreenWidget': OrderScreenWidget,
        'PosBookingCalendar': PosBookingCalendar
    }
});
