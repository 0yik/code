odoo.define('down_payment_pos.pos_deposit', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    // var floors = require('pos_restaurant.floors');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');

    var QWeb = core.qweb;
    var _t  = require('web.core')._t;



    var ListCustomerDepositScreen = screens.ScreenWidget.extend({
        template: 'ListCustomerDeposit',

        init: function(parent, options) {
            this._super(parent, options);
            var self = this;
        },

        show: function () {
            this._super();
            var self = this;
            var order = this.pos.get_order();
            var list_deposit = [];

            //next
            this.$el.find('.next').off().click(function () {
                var amount_total = order.get_total_with_tax();


                var list_choise = [];
                $('.customer-deposit-line.highlight').each(function () {
                    list_choise.push(parseInt($(this).attr('data-id')));
                });
                order.list_deposit_choice = [];
                list_deposit.forEach(function (item) {
                    if(list_choise.indexOf(item.id)!=-1){
                        order.list_deposit_choice.push(item);
                    }
                });

                var cashregisters = [];
                if(order.list_deposit_choice && order.list_deposit_choice.length > 0){

                    //remove all old payment lines

                    while(order.paymentlines.length>0){
                        order.paymentlines.remove(order.paymentlines.models[0]);
                    }

                    //add payment lines
                    order.list_deposit_choice.forEach(function (item) {
                        var cashregister = null;
                        for ( var i = 0; i < self.pos.cashregisters.length; i++ ) {
                            if ( self.pos.cashregisters[i].journal_id[0] === item.journal_id[0] ){
                                cashregister = self.pos.cashregisters[i];
                                cashregister.amount = item.remaining_amount;
                                let payment_date_split = item.payment_date.split('-');
                                cashregister.payment_date = new Date(payment_date_split[0],payment_date_split[1],payment_date_split[2]);
                                break;
                            }
                        }
                        if(!cashregister){
                            // cashregister. =
                            cashregister = Object.assign({}, self.pos.cashregisters[0]);
                            cashregister.journal_id = item.journal_id;
                            cashregister.amount = item.remaining_amount;
                            cashregister.payment_date = new Date(item.payment_date);
                        }
                        cashregister.deposit_id = item.id;
                        cashregisters.push(cashregister);

                    });
                    self.gui.show_screen('payment');
                    cashregisters.sort(function(a, b){
                        return a.payment_date.getTime()-b.payment_date.getTime()
                    });
                    for (var i=0;i<cashregisters.length;i++){
                        let item = cashregisters[i];
                        if(item){
                            if(item.amount >0 && amount_total>0){
                                order.add_paymentline( item );
                                if(item.amount > amount_total){
                                    order.paymentlines.models[order.paymentlines.length - 1].amount = amount_total;//temp, need fix
                                }else{
                                    order.paymentlines.models[order.paymentlines.length - 1].amount = item.amount;
                                }
                                order.paymentlines.models[order.paymentlines.length - 1].deposit = true;
                                order.paymentlines.models[order.paymentlines.length - 1].deposit_id = item.deposit_id;
                                amount_total = amount_total - item.amount;
                                self.gui.screen_instances.payment.reset_input();
                                self.gui.screen_instances.payment.render_paymentlines();
                            }
                        }
                    }
                }
            });

            //back
            this.$el.find('.button.back').click(function () {
                self.gui.show_screen('payment');
            });


            var account_payment = new Model('account.payment');
                account_payment.query(['id','communication','writeoff_account_id','journal_id','name','partner_id','payment_date','remaining_amount','amount','state'])
                 .filter([['is_deposit', '=', true],['remaining_amount','!=',0],['payment_type','=','inbound'],['partner_type','=','customer'],['state','=','posted']])
                 .limit(100)
                 .all().then(function (result) {
                    list_deposit = result;
                    self.render_customer_line(result);
                }
            );

            // new Model('account.payment').call('get_list_customer_deposit',[]).then(function (result) {
            //
            // });
        },
        render_element: function () {
            this._super();
        },
        render_customer_line : function (customers) {
            var render_node = this.$el[0].querySelector('.list-customer-deposit-line');
            render_node.innerHTML = '';
            var order = this.pos.get_order();
            var list_choice = order.list_deposit_choice;
            for (var i = 0, len = customers.length; i < len; i++){
                var customer = customers[i];

                var customerline_html = QWeb.render('CustomerDepositLine', {
                    widget: this,
                    item: customer
                });
                var customerline = document.createElement('tbody');
                customerline.innerHTML = customerline_html;
                customerline = customerline.childNodes[1];

                customerline.addEventListener('click', function() {
                    $(this).toggleClass('highlight');

                });

                render_node.appendChild(customerline);
                if(list_choice){
                    var hightlights = list_choice.find(function (item) {
                        return item.id == customer.id;
                    });
                    if(hightlights){
                        $('tr.customer-deposit-line[data-id="'+hightlights.id+'"]').addClass('highlight');
                    }
                }

            }
        }
    });

    gui.define_screen({
    'name': 'listcustomerdepositscreen',
    'widget': ListCustomerDepositScreen,
    'condition': function(){
        return true;
    },
    });

    screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();

            this.$('.js_deposit').click(function(){
                self.gui.show_screen('listcustomerdepositscreen', {
                });
            });
        },
        finalize_validation:function () {
            var self = this;
            var order = this.pos.get_order();
            var paymentlines = order.paymentlines;
            var data = [];
            paymentlines.models.forEach(function (item) {
                if(item.deposit){
                    data.push({
                        'id':item.deposit_id,
                        'amount': item.amount
                    })
                }
            });
            new Model('account.payment').call('update_amount_payment',[data]).then(function (result) {
                if(result.code == 200){
                    console.log('sync amount successfully');
                }else{
                    alert('sync amount error');
                }

            });
            this._super();
        },
    });
    screens.ClientListScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();

            this.$('.create_deposit').click(function(){
                if($('tr.client-line.highlight').length>0){
                    self.pos.selected_partner_id = $('tr.client-line.highlight').attr('data-id');
                    self.gui.show_screen('createcustomerdepositscreen');
                }

            });
        },
        show: function (options) {
            this._super(options);
            var self = this;
            this.$('.back').off().click(function(){
                self.gui.show_screen('payment');
            });
            if(self.$el.find('.button.next').hasClass('oe_hidden')){
                self.$el.find('.button.create_deposit').addClass('oe_hidden');
            }else{
                self.$el.find('.button.create_deposit').removeClass('oe_hidden');
            }
        },
        line_select:function (event,$line,id) {
            var self = this;

            this._super(event,$line,id);
            if ($line.hasClass('highlight')){
                self.$el.find('.button.create_deposit').removeClass('oe_hidden');
            }else{
                self.$el.find('.button.create_deposit').addClass('oe_hidden');
            }
        }
    });
    return ListCustomerDepositScreen;
});