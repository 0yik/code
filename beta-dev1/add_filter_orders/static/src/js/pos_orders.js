odoo.define('add_filter_orders.pos_orders', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var models = require('point_of_sale.models');

    models.load_fields('pos.config', ['time_order', 'number_of_order']);



    var OrdersScreenWidget;
    _.each(gui.Gui.prototype.screen_classes, function (o) {
        if (o.name == 'wk_order') {
            OrdersScreenWidget = o.widget;
            OrdersScreenWidget.include({
                orderline_click_handler: function (e) {
                    $(e.target)
                },
                show: function () {
                    this._super();
                    var self = this;
                },
                filter_order: function (orders) {
                    var i=0;
                    var self = this;
                    var number_order = this.pos.config.number_of_order;
                    //var max_date = new Date(this.pos.config.time_order*60*60*1000);
                    //if(number_order > 0 && max_date > 0){
                    //var diff_day = new Date(new Date() - new Date(order.date_order));
                    var new_order = _.filter(orders, function (order) {
                        return i++ < number_order;
                    });
                    return new_order;
                },
                render_list: function(order, input_txt) {
                    order = this.filter_order(order);
                    var self = this;
                    var customer_id = this.get_customer();
                    var new_order_data = [];
                    if (customer_id != undefined) {
                        for (var i = 0; i < order.length; i++) {
                            if (order[i].partner_id[0] == customer_id)
                                new_order_data = new_order_data.concat(order[i]);
                        }
                        order = new_order_data;
                    }
                    if (input_txt != undefined && input_txt != '') {
                        var new_order_data = [];
                        var search_text = input_txt.toLowerCase()
                        for (var i = 0; i < order.length; i++) {
                            if (order[i].partner_id == '') {
                                order[i].partner_id = [0, '-'];
                            }
                            if (((order[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                                new_order_data = new_order_data.concat(order[i]);
                            }
                        }
                        order = new_order_data;
                    }
                    var contents = this.$el[0].querySelector('.wk-order-list-contents');
                    contents.innerHTML = "";
                    var wk_orders = order;
                    for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
                        var wk_order = wk_orders[i];
                        var orderline_html = QWeb.render('WkOrderLine', {
                            widget: this,
                            order: wk_orders[i],
                            customer_id: wk_orders[i].partner_id[0],
                        });
                        var orderline = document.createElement('tbody');
                        orderline.innerHTML = orderline_html;
                        orderline = orderline.childNodes[1];
                        //orderline.addEventListener('click',this.orderline_click_handler);
                        contents.appendChild(orderline);
                    }

                },
                display_order_details: function(visibility, order, clickpos) {
                    var self = this;
                    var contents = this.$('.order-details-contents');
                    var parent = this.$('.wk_order_list').parent();
                    var scroll = parent.scrollTop();
                    var height = contents.height();
                    var orderlines = [];
                    var statements = [];
                    var journal_ids_used = [];
                    if (visibility === 'show') {
                        order.lines.forEach(function(line_id) {
                            orderlines.push(self.pos.db.line_by_id[line_id]);
                        });
                        order.statement_ids.forEach(function(statement_id) {
                            var statement = self.pos.db.statement_by_id[statement_id];
                            statements.push(statement);
                            journal_ids_used.push(statement.journal_id[0]);
                        });
                        contents.empty();
                        contents.append($(QWeb.render('OrderDetails', { widget: this, order: order, orderlines: orderlines, statements: statements })));
                        var new_height = contents.height();
                        if (!this.details_visible) {
                            if (clickpos < scroll + new_height + 20) {
                                parent.scrollTop(clickpos - 20);
                            } else {
                                parent.scrollTop(parent.scrollTop() + new_height);
                            }
                        } else {
                            parent.scrollTop(parent.scrollTop() - height + new_height);
                        }
                        this.details_visible = true;
                        self.$("#close_order_details").on("click", function() {
                            self.selected_tr_element.removeClass('highlight');
                            self.selected_tr_element.addClass('lowlight');
                            self.details_visible = false;
                            self.display_order_details('hide', null);
                        });
                        self.$("#wk_refund").on("click", function() {
                            var order_list = self.pos.db.pos_all_orders;
                            var order_line_data = self.pos.db.pos_all_order_lines;
                            var order_id = this.id;
                            var message = '';
                            var non_returnable_products = false;
                            var original_orderlines = [];
                            var allow_return = true;
                            var max_date = new Date(self.pos.config.time_order*60*60*1000);
                            var diff_day = new Date(new Date() - new Date(order.date_order))
                            if(order.return_status == 'Fully-Returned'){
                                message = 'No items are left to return for this order!!'
                                allow_return = false;
                            }
                            if(diff_day > max_date){
                                message = 'You can not refund an expired order!!'
                                allow_return = false;
                            }
                            if (allow_return) {
                                order.lines.forEach(function(line_id){
                                    var line = self.pos.db.line_by_id[line_id];
                                    var product = self.pos.db.get_product_by_id(line.product_id[0]);
                                    if(product == null){
                                        non_returnable_products = true;
                                        message = 'Some product(s) of this order are unavailable in Point Of Sale, do you wish to return other products?'
                                    }
                                    else if (product.not_returnable) {
                                        non_returnable_products = true;
                                        message = 'This order contains some Non-Returnable products, do you wish to return other products?'
                                    }
                                    else if(line.qty - line.line_qty_returned > 0)
                                        original_orderlines.push(line);
                                });
                                if(original_orderlines.length == 0){
                                    self.gui.show_popup('my_message',{
                                        'title': _t('Cannot Return This Order!!!'),
                                        'body': _t("There are no returnable products left for this order. Maybe the products are Non-Returnable or unavailable in Point Of Sale!!"),
                                    });
                                }
                                else if(non_returnable_products){
                                    self.gui.show_popup('confirm',{
                                        'title': _t('Warning !!!'),
                                        'body': _t(message),
                                        confirm: function(){
                                            self.gui.show_popup('return_products_popup',{
                                                'orderlines': original_orderlines,
                                                'order':order,
                                                'is_partial_return':true,
                                            });
                                        },
                                    });
                                }
                                else{
                                    self.gui.show_popup('return_products_popup',{
                                        'orderlines': original_orderlines,
                                        'order':order,
                                        'is_partial_return':false,
                                    });
                                }
                            }
                            else
                            {
                                self.gui.show_popup('my_message',{
                                    'title': _t('Warning!!!'),
                                    'body': _t(message),
                                });
                            }
                        });
                    }
                    if (visibility === 'hide') {
                        contents.empty();
                        if (height > scroll) {
                            contents.css({ height: height + 'px' });
                            contents.animate({ height: 0 }, 400, function() {
                                contents.css({ height: '' });
                            });
                        } else {
                            parent.scrollTop(parent.scrollTop() - height);
                        }
                        this.details_visible = false;
                    }
                },
            })
        }
    });
});
