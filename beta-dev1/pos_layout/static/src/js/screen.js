odoo.define('pos_layout.pos_update_layout', function (require) {
    "use strict";

    var formats = require('web.formats');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var round_di = utils.round_decimals;
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var popups = require('point_of_sale.popups');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            var self = this;
            var res = _super_order.initialize.apply(this, arguments);
            // setInterval(function () {
            //     self.auto_build_promotion();
            //     console.log('auto build promotion');
            // }, 8000);
            return res;
        }
    });


    screens.ProductScreenWidget.include({
        start: function () {
            var self = this;
            this._super();
            this.$('.control-buttons').addClass('oe_hidden');
            this.$('#all_orders').addClass('oe_hidden');
            // for (var i = 0; i < Object.keys(this.action_buttons).length; i++) {
            //     var widget = this.action_buttons[Object.keys(this.action_buttons)[i]];
            //     widget.appendTo($('.control-buttons'));
            // }
        },
        click_product: function(product) {
            if(product) this._super(product);
        },
        show: function() {
            this._super();
            // this.pos.auto_promotion = true;
            this.pos.category == 'delivery' ? this.$('.btn-create-so').show() : this.$('.btn-create-so').hide();
            this.pos.category == 'dive_in' ? this.$('.btn-assign-order').show() : this.$('.btn-assign-order').hide();
            this.pos.category == 'dive_in' ? this.$('.seat_number_btn').show() : this.$('.seat_number_btn').hide();
            $('.product-screen').css('bottom', $('.button-transaction').height());
        },
        renderElement: function() {
            var self = this;
            this._super();

            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });

                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });

            this.$('.guest-button').click(function() {
                self.gui.show_popup('number', {
                    'title':  _t('Guests ?'),
                    'cheap': true,
                    'value':   self.pos.get_order().customer_count,
                    'confirm': function(value) {
                        value = Math.max(1,Number(value));
                        self.pos.get_order().set_customer_count(value);
                        $('button.guest-button .guest_number').text(value);
                        //self.renderElement();
                    },
                });
            });

            this.$('.order-submit').click(function(){
                self.submit_order();
                self.pos.get_order().table.latest_order = new Date().toLocaleTimeString();
                self.gui.show_popup('optionpopup', {
                    'title': "LET'S GET STARTED",
                });
            });

            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });

            this.$('.btn-create-so').click(function(){
                self.click_create_so();
            });

            this.$('.transfer-button').click(function(){
                self.pos.transfer_order_to_different_table();
            });

            this.$('.btn-coupon').click(function(){
                self.gui.show_popup('select_existing_popup_widget', {});
            });

            this.$('.btn-reward').click(function(){
                self.click_reward();
            });

            this.$('.btn-assign-order').click(function(){
                self.click_assign_order();
            });

            this.$('.btn-removeline').click(function(){
                self.remove_selected_line();
            });

            this.$('.btn-backspace').click(function(){
                self.click_backspace();
            });

            this.$('.branch_btn').click(function(){
                self.click_branch();
            });

            this.$('.seat_number_btn').click(function(){
                self.click_seat_number();
            });
        },
        seatnumber: function() {
           if (this.pos.get_order()) {
               return this.pos.get_order().seat_number || 0;
           } else {
               return 0;
           }
         },
        click_backspace: function() {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()){
                order.get_selected_orderline().set_quantity('remove');
            }
         },

        click_seat_number: function () {
            var self = this;
           if (this.pos.get_order().get_selected_orderline()){
               var seat_number = this.pos.get_order().get_selected_orderline().seat_number;
           } else{
               var seat_number = this.pos.get_order().seat_number;
           }
           this.gui.show_popup('number', {
               'title':  _t('Number of Seats ?'),
               'cheap': true,
               'value':  seat_number,
               'confirm': function(value) {
                   self.pos.get_order().set_seat_number_count(value);
                   self.update_seat_number_view();
               },
           });
        },
        update_seat_number_view: function () {
            this.$('.seat_number_btn span').text(this.seatnumber());
            this.$('.seat_position span').text(this.seatnumber());
        },
        submit_order: function () {
            var order = this.pos.get_order();
            if(order && order.hasChangesToPrint()){
                order.printChanges();
                order.saveChanges();
            }
        },
        click_branch: function () {
            this.gui.show_popup('branhoptionspopup', {
                'title': _t("SELECT BRANCH"),
            });
        },
        click_create_so: function () {
            var self = this;
            var order = this.pos.get('selectedOrder');
            var client = order.get_client();
            var orderLine = order.orderlines;
            if (orderLine.length == 0) {
                this.pos.gui.show_popup('pos_to_sale_order_custom_message', {
                    'title': _t("Orderline Empty"),
                    'body': _t("There is no product in selected Order."),
                });
            } else if (client == null) {
                this.gui.show_popup('confirm', {
                    'title': _t('Please select the Customer'),
                    'body': _t('You need to select the customer first.'),
                    confirm: function() {
                        self.gui.show_screen('clientlist');
                    },
                });
            } else {
                this.gui.show_popup('Create_Sales_Order_popup_widget', {});
            }
        },
        get_current_branch: function () {
           return this.pos.get_order() && this.pos.get_order().branch_id ? this.pos.get_order().branch_id : this.pos.config.branch_id[1];
        },
        remove_selected_line: function () {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()){
                order.remove_orderline(order.get_selected_orderline());
            }
        },
        click_reward: function () {
            var order  = this.pos.get_order();
            var client = order.get_client();
            if (!client) {
                this.gui.show_screen('clientlist');
                return;
            }
            try {
                var rewards = order.get_available_rewards();
            } catch (err){
                console.log(err);
                var rewards = [];
            }
            if (rewards.length === 0) {
                this.gui.show_popup('alert',{
                    'title': 'No Rewards Available',
                    'body':  'There are no rewards available for this customer as part of the loyalty program',
                });
                return;
            } else if (rewards.length === 1 && this.pos.loyalty.rewards.length === 1) {
                order.apply_reward(rewards[0]);
                return;
            } else {
                var list = [];
                for (var i = 0; i < rewards.length; i++) {
                    list.push({
                        label: rewards[i].name,
                        item:  rewards[i],
                    });
                }
                this.gui.show_popup('selection',{
                    'title': 'Please select a reward',
                    'list': list,
                    'confirm': function(reward){
                        order.apply_reward(reward);
                    },
                });
            }
        },
        click_assign_order: function () {
            this.pos.gui.show_screen('temp_order', {});
        },
        guests: function() {
            if (this.pos.get_order()) {
                return this.pos.get_order().customer_count;
            } else {
                return 0;
            }
        },
        format_float: function(value, decimals){
            decimals = decimals || 0;
            return formats.format_value(round_di(value, decimals), {
                    type: 'float',
                    digits: [69, decimals]
                })
        },
        format_currency_custom: function(amount,precision){
            var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};

            amount = this.format_float(amount,precision);

            if (currency.position === 'after') {
                return amount + ' ' + (currency.symbol || '');
            } else {
                return (currency.symbol || '') + ' ' + amount;
            }
        },
        update_customer_view: function () {
            this.$('.set-customer .client-name').text(this.pos.get_client() && this.pos.get_client().name || 'Customer');
        },
        update_transaction_view: function () {
            var order = this.pos.get_order();
            if(order){
                order.total_quantity = 0;
                order.orderlines.models.forEach(x=> order.total_quantity += x.quantity);

                this.$('.total_qty .arrange-bottom').text(this.format_float(order.total_quantity));
                this.$('.total_price .arrange-bottom').text(this.format_currency_custom(order.get_total_without_tax()));
                this.$('.total_tax .arrange-bottom').text(this.format_currency_custom(order.get_total_tax()));
                this.$('.total_discount .arrange-bottom').text(this.format_currency_custom(order.get_total_discount()));
                this.$('.total_amount .arrange-bottom').text(this.format_currency_custom(order.get_total_with_tax()));

                var changes = order.hasChangesToPrint();
                var skipped = changes ? false : order.hasSkippedChanges();

                this.$('.order-submit').toggleClass('highlight', !!changes);
                this.$('.order-submit').toggleClass('altlight', !!skipped);
            }

        }
    });

    screens.OrderWidget.include({
        update_summary: function() {
            this._super();
            var product_widget = this.pos.gui.screen_instances["products"];
            if(product_widget) product_widget.update_transaction_view();
        },
        format_float: function(value, decimals){
            decimals = decimals || 0;
            return formats.format_value(round_di(value, decimals), {
                    type: 'float',
                    digits: [69, decimals]
                })
        },
        format_currency_custom: function(amount,precision){
            var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: precision};

            amount = this.format_float(amount,precision);

            if (currency.position === 'after') {
                return amount + ' ' + (currency.symbol || '');
            } else {
                return (currency.symbol || '') + ' ' + amount;
            }
        },
    });

    screens.PaymentScreenWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.keyboard_keydown_handler = function(event){

                if (event.target.id == 'coupon_code') {
                    return;
                }
                if (event.keyCode === 8 || event.keyCode === 46) { // Backspace and Delete
                    event.preventDefault();

                    // These do not generate keypress events in
                    // Chrom{e,ium}. Even if they did, we just called
                    // preventDefault which will cancel any keypress that
                    // would normally follow. So we call keyboard_handler
                    // explicitly with this keydown event.
                    self.keyboard_handler(event);
                }
            };
            this.keyboard_handler = function(event){
                if (event.target.id == 'coupon_code') {
                    return;
                }
                var key = '';
                if (event.type === "keypress") {
                    if (event.keyCode === 13) { // Enter
                        self.validate_order();
                    } else if ( event.keyCode === 190 || // Dot
                                event.keyCode === 110 ||  // Decimal point (numpad)
                                event.keyCode === 188 ||  // Comma
                                event.keyCode === 46 ) {  // Numpad dot
                        key = self.decimal_point;
                    } else if (event.keyCode >= 48 && event.keyCode <= 57) { // Numbers
                        key = '' + (event.keyCode - 48);
                    } else if (event.keyCode === 45) { // Minus
                        key = '-';
                    } else if (event.keyCode === 43) { // Plus
                        key = '+';
                    }
                } else { // keyup/keydown
                    if (event.keyCode === 46) { // Delete
                        key = 'CLEAR';
                    } else if (event.keyCode === 8) { // Backspace
                        key = 'BACKSPACE';
                    }
                }
                self.payment_input(key);
                event.preventDefault();
            };
        },
        show: function() {
            var self = this;
            this._super();
            var order = self.pos.get_order();
            if (order) {
                self.$('.pos-receipt-payment').html(QWeb.render('PaymentReceipt',{
                    widget:self,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                }));
            }
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.btn-coupon-payment').click(function(){
                self.gui.show_popup('coupon_popup_widget', {});
            });
        },
    });

    var CouponPopupWidget = popups.extend({
        template: 'CouponPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
            var self = this;
            this._super(options);

        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var selectedOrder = self.pos.get('selectedOrder');
            this.$('#apply_coupon_code').click(function() {
                //console.log("create-new-couponnnnnnnnnnnnn callleddddddddddddd")
                var entered_code = $("#coupon_code").val();
                //console.log("##################entered_code", entered_code);
                var partner_id = false
                if (order.get_client() != null)
                    partner_id = order.get_client();
                //console.log("parterrrrrrrrrrrrrrrrrrr", partner_id);

                (new Model('pos.gift.coupon')).call('existing_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                    //alert('Connection Error. Try again later !!!!');
                }).done(function(output) {

                    //console.log("outputttttttttttttttttttttt", output, partner_id)

                    var orderlines = order.orderlines;
                    //console.log("#######################orderlines", orderlines)
                    //console.log("**************************", entered_code)



                    // Popup Occurs when no Customer is selected...
                    if (!partner_id) {
                        self.gui.show_popup('error', {
                            'title': _t('Unknown customer'),
                            'body': _t('You cannot use Coupons/Gift Voucher. Select customer first.'),
                        });
                        return;
                    }

                    // Popup Occurs when not a single product in orderline...
                    if (orderlines.length === 0) {
                        self.gui.show_popup('error', {
                            'title': _t('Empty Order'),
                            'body': _t('There must be at least one product in your order before it can be apply for voucher code.'),
                        });
                        return;
                    }

                    // Goes inside when atleast product in orderline...
                    if (orderlines.models.length) {
                        // Condition True when Entered Code & Backend Coupon code will be same...
                        if (output == 'true') {
                            var selectedOrder = self.pos.get('selectedOrder');
                            //console.log("ifffffffffffffff selectedOrderrrrrrrrrrrrrrrrrrrrrrrrrr", selectedOrder)
                            selectedOrder.coupon_id = entered_code;
                            //console.log("coupon_iddddddddddddddddddddddddd", selectedOrder.coupon_id)
                            var total_amount = selectedOrder.get_total_without_tax();
                            //console.log("totallllllllllllllllllllllllllllllllllllll", total_amount)

                            // Read Method to find appllied coupon's amount
                            new Model('pos.gift.coupon').call('search_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                                //console.log("search_coupon callledddddddddddddddddddd")
                            }).done(function(output) {
                                //console.log("1111111111111111111111111outputttttttttttttttttttttt", output)
                                var amount = output[1];
                                //console.log("amounttttttttttttttttt_iddddddddddddddddddddddddd", amount)
                                var total_val = total_amount - amount;
                                //console.log("tttttttttttttttttttttttttttttotal", total_val)
                                var product_id = self.pos.pos_coupons_setting[0].product_id[0];
                                //console.log("productttttttttt_iddddddddddddddddddddddddd", product_id)


                                var product = self.pos.db.get_product_by_id(product_id);
                                //console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@product", product)
                                var selectedOrder = self.pos.get('selectedOrder');

                                selectedOrder.add_product(product, {
                                    price: -amount
                                });
                                $('.paymentlines-empty .total').html(self.format_currency(selectedOrder.get_total_with_tax()));
                                $('.pos-receipt-payment').html('');
                                $('.pos-receipt-payment').html(QWeb.render('PaymentReceipt',{
                                    widget:self,
                                    order: selectedOrder,
                                    receipt: selectedOrder.export_for_printing(),
                                    orderlines: selectedOrder.get_orderlines(),
                                    paymentlines: selectedOrder.get_paymentlines(),
                                }));
                            });
                        } else { //Invalid Coupon Code
                            self.gui.show_popup('error', {
                                'title': _t('Invalid Code !!!'),
                                'body': _t("Voucher Code Entered by you is Invalid. Enter Valid Code..."),
                            });
                        }

                    } else { // Popup Shows, you can't use more than one Voucher Code in single order.
                        self.gui.show_popup('error', {
                            'title': _t('Already Used !!!'),
                            'body': _t("You have already use this Coupon code, at a time you can use one coupon in a Single Order"),
                        });
                    }

                });
            });


        },

    });
    gui.define_popup({
        name: 'coupon_popup_widget',
        widget: CouponPopupWidget
    });

    _.each(gui.Gui.prototype.screen_classes, function (o) {
        if (o.name == 'splitbill') {
            o.widget.include({
                format_float: function(value, decimals){
                    decimals = decimals || 0;
                    return formats.format_value(round_di(value, decimals), {
                            type: 'float',
                            digits: [69, decimals]
                        })
                },
                format_currency_custom: function(amount,precision){
                    var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};

                    amount = this.format_float(amount,precision);

                    if (currency.position === 'after') {
                        return amount + ' ' + (currency.symbol || '');
                    } else {
                        return (currency.symbol || '') + ' ' + amount;
                    }
                },
            });
        }
    });
});
