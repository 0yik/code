odoo.define('pos_so_payments.so_payment_widget', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var Model = require('web.Model');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var QWeb = core.qweb;
    /*--------------------------------------*\
     |         THE SO PAYMENT SCREEN           |
    \*======================================*/

    // The Payment Screen handles the payments, and
    // it is unfortunately quite complicated.

    var PaymentSOScreenWidget = screens.ScreenWidget.extend({
        template: 'PaymentSOScreenWidget',
        back_screen: 'product',
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);

            this.pos.bind('change:selectedOrder', function () {
                this.renderElement();
            }, this);

            this.inputbuffer = "";
            this.firstinput = true;
            this.keyboard_keydown_handler = function (event) {
                if (event.keyCode === 8 || event.keyCode === 46) { // Backspace and Delete
                    event.preventDefault();
                    self.keyboard_handler(event);
                }
            };

            this.keyboard_handler = function (event) {
                var key = '';

                if (event.type === "keypress") {
                    if (event.keyCode === 13) { // Enter
                        self.validate_order();
                    } else if (event.keyCode === 190 || // Dot
                        event.keyCode === 110 ||  // Decimal point (numpad)
                        event.keyCode === 188 ||  // Comma
                        event.keyCode === 46) {  // Numpad dot
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
        // resets the current input buffer
        reset_input: function () {
            this.firstinput = true;
            this.inputbuffer = "";
        },
        // handle both keyboard and numpad input. Accepts
        // a string that represents the key pressed.
        payment_input: function (input) {
            if(input != undefined){
                var newbuf = this.gui.numpad_input(this.inputbuffer, input, {'firstinput': this.firstinput});

                this.firstinput = (newbuf.length === 0);

                // popup block inputs to prevent sneak editing.
                if (this.gui.has_popup()) {
                    return;
                }

                if (newbuf !== this.inputbuffer) {
                    this.inputbuffer = newbuf;
                    var amount = this.inputbuffer;
                    this.$('.payment_input input').val(this.format_currency_no_symbol(amount));
                }
                if(this.is_valid_payment_invoice()){
                    this.$('.next').addClass('highlight');
                }else{
                    this.$('.next').removeClass('highlight');
                }
            }
        },
        click_numpad: function (button) {
            this.payment_input(button.data('action'));
        },
        click_back: function () {
            this.gui.show_screen('products');
        },
        render_numpad: function() {
            var self = this;
            var numpad = $(QWeb.render('PaymentScreen-Numpad', { widget:this }));
            numpad.on('click','button',function(){
                self.click_numpad($(this));
            });
            return numpad;
        },
        renderElement: function () {
            var self = this;
            this._super();

            this.$('.back').click(function () {
                self.click_back();
            });
            this.$('.next').click(function () {
                self.validate_order();
            });
        },
        show: function () {
            this.reset_input();
            window.document.body.addEventListener('keypress', this.keyboard_handler);
            window.document.body.addEventListener('keydown', this.keyboard_keydown_handler);
            this._super();
            var numpad = this.render_numpad();
            numpad.appendTo(this.$('.payment-numpad'));
            this.$('.payment_date input').val(new Date().toISOString().slice(0,10).replace(/-/g,"-"));
            this.$('.order_amount span').text(this.format_currency(this.pos.get_so_invoice_total()));
        },
        hide: function () {
            window.document.body.removeEventListener('keypress', this.keyboard_handler);
            window.document.body.removeEventListener('keydown', this.keyboard_keydown_handler);
            this._super();
        },
        is_valid_payment_invoice: function () {
            var total = parseFloat(this.pos.get_so_invoice_total());
            var payment_amount = parseFloat(this.$('.payment_input input').val());
            return payment_amount >= total;
        },
        validate_order: function () {
            console.log('payment');
            var self = this;
            if(this.is_valid_payment_invoice()){
                var account_invoice = new Model('account.invoice');
                var journal_id = this.$('.payment_journal option:selected').val();
                var payment_amount = this.$('.payment_input input').val();
                var payment_date = this.$('.payment_date input').val();
                account_invoice.call('payment_invoice', [this.pos.get_so_invoice().invoice_ids, journal_id, payment_amount, payment_date])
                .then(function(result) {
                    if(result.status){
                        self.gui.show_screen('products');
                    }
                    else{
                        alert(result.message);
                    }
                });
            }
            else {
                alert("Invalid Payment");
            }
        },
    });
    gui.define_screen({name: 'payment_so', widget: PaymentSOScreenWidget});
});
