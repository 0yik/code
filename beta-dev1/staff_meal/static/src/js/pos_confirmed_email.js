odoo.define('staff_meal.pos_confirmed_email', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;
var Model = require('web.Model');

var ListPaymentConfirmScreenWidget = screens.ScreenWidget.extend({
    template: 'ListPaymentConfirmScreenWidget',

    init: function(parent, options) {
        this._super(parent, options);
    },

    show: function () {
        var self = this;
        this.pos.category = 'staff_meal';
        this._super();
        this.$el.find('.next').click(function () {
            if(self.$el.find('tr.payment-line.highlight').length > 0){
                var id = self.$el.find('tr.payment-line.highlight').attr('data-id');

                var element_button = $(this);
                element_button.hide();

                var table_id = Object.keys(self.pos.tables_by_id)[0];
                var table = self.pos.tables_by_id[table_id];
                self.pos.table = table;

                self.pos.add_new_order();
                self.gui.show_screen('listpayment');
                var temp_order = self.pos.get_order();
                temp_order.all_free = true;
                temp_order.category = 'staff_meal';
                temp_order.popup_option = 'Staff Meal';
                temp_order.remove_from_summary = false;
                temp_order.saved_resume = temp_order.build_line_resume();
                temp_order.order_payment_confirm_id = id;
                self.gui.screen_instances.payment.$('.next').hide();
                var orderline = new Model('pos.order.line');
                    orderline.query(['id','product_id', 'name','qty'])
                     .filter([['order_id', '=', parseInt(id)]])
                     .limit(100)
                     .all().then(function (data) {
                        for(var i=0;i<data.length;i++){
                            var product = self.pos.db.get_product_by_id(data[i].product_id[0]);
                            temp_order.add_product(product);
                            var orderline = temp_order.get_orderlines();
                            orderline[orderline.length-1].set_quantity(parseInt(data[i].qty));
                        }
                        self.pos.set('selectedOrder', temp_order);
                        self.pos.set_order(temp_order);
                        self.gui.screen_instances.payment.$('.next').show();
                        self.gui.show_screen('payment');

                        temp_order.add_staff_meal_paymentline();

                        element_button.show();
                        self.gui.screen_instances.payment.$('.next').off().click(function () {
                            if(self.pos.category == 'staff_meal'){
                                $('button.send_kitchen').click();
                            }
                            self.gui.current_screen.validate_order();
                        });
                        $('.payment-numpad button.number-char').prop('disabled', true);
                        $('.payment-numpad button.numpad-char').prop('disabled', true);
                        $('.payment-numpad button.mode-button').prop('disabled', true);
                        $('.payment-numpad button.numpad-backspace').prop('disabled', true);
                        $('.paymentmethods').hide();
                    }
                );



            }
        });
        this.$el.find('.button.back').click(function () {
            self.gui.show_popup('optionpopup', {
                'title': "LET'S GET STARTED",
            });
        });
        self.load_payment();
    },

    load_payment: function () {
        var self = this;
        var pos_order = new Model('pos.order');
        pos_order.call('get_list_payment_confirm',[]).then(function (result) {
            console.log('result');
            self.render_payment(result);
        });
    },
    render_payment : function (orders) {
        var render_node = this.$el[0].querySelector('.payment-list-contents');
        render_node.innerHTML = '';
        for (var i = 0, len = orders.length; i < len; i++){
            var order = orders[i];

            var orderline_html = QWeb.render('PaymentLineComfirm', {
                widget: this,
                item: order
            });
            var paymentline = document.createElement('tbody');
            paymentline.innerHTML = orderline_html;
            paymentline = paymentline.childNodes[1];

            paymentline.addEventListener('click', function() {
                if($(this).hasClass('highlight')){
                    $('tr.payment-line').removeClass('highlight');
                }else{
                    $('tr.payment-line').removeClass('highlight');
                    $(this).addClass('highlight');
                }

            });
            render_node.appendChild(paymentline);

        }

    }


});

gui.define_screen({
    'name': 'listpayment',
    'widget': ListPaymentConfirmScreenWidget,
    'condition': function(){
        return true;
    },
});

screens.PaymentScreenWidget.include({
    validate_order: function (force_validation) {
        var self = this;
        var order = this.pos.get('selectedOrder');
        // order.receipt_free = true;
        if (order.popup_option =='Staff Meal' && order.order_payment_confirm_id) {
            var pos_order_model = new Model('pos.order');
                return pos_order_model.call('paid_order_open', [order.order_payment_confirm_id])
                .then(function (result) {
                    self.gui.show_screen('receipt');
                    var order = self.pos.get_order();
                    var func = self.gui.current_screen.$('.next').click;
                    self.gui.current_screen.$('.next').off().click(function(){
                        self.$('.next').on( "click", func );
                        if (order) {
                            self.pos.delete_current_order();
                        }
                        self.$('.next').on( "click", func );

                        self.gui.show_popup('staffmealoptionpopup', {
                            'title': "LET'S GET STARTED",
                        });
                    });
                });
        }else {
            return this._super(force_validation);
        }
    },
});
// gui.Gui = gui.Gui.extend({
//     show_screen: function(screen_name,params,refresh) {
//         var self = this;
//         if(this.pos.category == 'staff_meal' && screen_name == 'receipt'){
//             // var order = this.pos.get_order();
//             // if(order.paymentlines.length>0){
//             //     order.paymentlines.models[0].amount = 0;
//             // }
//             // order.receipt_free = true;
//         }
//         self._super(screen_name,params,refresh);
//         if(this.pos.category == 'staff_meal' && screen_name == 'receipt'){
//             self.screen_instances.receipt.$('.button.next.highlight').click(function () {
//                 self.show_popup('optionpopup', {
//                     'title': "LET'S GET STARTED",
//                 });
//             })
//         }
//     }
// });
});

