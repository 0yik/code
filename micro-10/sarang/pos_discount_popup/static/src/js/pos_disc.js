odoo.define('pos_discount_popup.pos_discount_popup', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Session = require('web.Session');
    var PosDB = require('point_of_sale.DB');
    var QWeb = core.qweb;
    var mixins = core.mixins;
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var _t  = require('web.core')._t;
    var utils = require('web.utils');
    var main_discount = 0;
    var round_pr = utils.round_precision;
    var PaymentScreenWidget = screens.PaymentScreenWidget;
    var PopupWidget = require('point_of_sale.popups');
    var ProductScreenWidget = screens.ProductScreenWidget;
    models.load_fields('product.product','product_addon_ids');
    models.load_fields('product.product','num_of_addon');


    var DiscPopupWidget = PopupWidget.extend({
        template: 'DiscManager',
        show: function (options) {
            var order    = this.pos.get_order();
            if (!order.get_orderlines().length) {
                alert('Please choose product first');
                return;
            }
            var self = this;
            this._super(options);
            options = options || {};

            this.inputbuffer = '' + (options.value   || '');
            this.decimal_separator = _t.database.parameters.decimal_point;
            this.renderElement();
            this.firstinput = true;

            this.show_button();
            //set button active
            $('button.numb-discount').click(function (event) {
                self.click_button_discount(event);
            });
            var discount = order.get_selected_orderline().get_discount();
            if (discount){
                $('button.numb-discount').each(function () {
                    if($(this).attr('data-id').trim() == discount){
                        $(this).addClass('active btn-fill');
                    }
                });
                $('.discount-value').text(discount.toString().trim());
            }

        },
        show_button:function () {
            var self = this;
            var listbutton = [];
            if(this.pos.config.discount_amount){
                var listbutton = this.pos.config.discount_amount.split(',').filter(item => item.length <3 && parseInt(item));
            }
            var render_node = self.$el[0].querySelector('.render-button-discount');
            render_node.innerHTML = "";
            var customer_html = QWeb.render('ListButtonDiscount', {
                listbutton: listbutton
            });
            var div = document.createElement('div');
            div.innerHTML = customer_html;
            $(render_node).replaceWith($(div));
        },

        events: {
            'click .button.cancel':  'click_cancel',
            'click .button.confirm': 'click_confirm',
            'click .cancel-disc':   'click_cancel_disc',
        },
        click_cancel_disc:function () {
            var order    = this.pos.get_order();
            if (!order.get_orderlines().length) {
                return;
            }
            order.get_selected_orderline().set_discount(0);

            this.gui.close_popup();
        },
        click_button_discount: function(event) {

            var self = this;
            var def  = new $.Deferred();
            var list = [];

            var newbuf = this.gui.numpad_input(this.inputbuffer, 'CLEAR', {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);

            if (newbuf !== this.inputbuffer) {
               this.inputbuffer = newbuf;
               this.$('.discount-value').text(this.inputbuffer);
            }
            var newbuf = this.gui.numpad_input(this.inputbuffer, $(event.target).attr('data-id'), {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);

            if (newbuf !== this.inputbuffer) {
               this.inputbuffer = newbuf;
               this.$('.discount-value').text(this.inputbuffer);
            }
            //remove active
            $('button.numb-discount').each(function () {
                $(this).removeClass('active btn-fill');
            });
            // add new active
            $(event.currentTarget).addClass('active btn-fill');
        },
        click_confirm: function(){
            this.gui.close_popup();
            if( this.options.confirm ){
                this.options.confirm.call(this,this.inputbuffer);
            }

        },
        click_cancel: function(){
            this.gui.close_popup();
        },
    });

    gui.define_popup({name:'transaction', widget:DiscPopupWidget});
    models.load_fields("pos.config", "discount_amount");

    var DiscountAll = screens.ActionButtonWidget.extend({
        template: 'DiscountAll',
        init: function(parent) {
            this._super(parent);
        },

        button_click: function(){
            var self = this;
            var def  = new $.Deferred();
            var list = [];


            self.gui.show_popup('transaction', {
                'title': 'Discount Percentage',
                transaction: list,
                'confirm': function(val) {

                    val = Math.round(Math.max(0,Math.min(100,val)));
                    self.apply_discount(val);
                },
            });
        },
        apply_discount: function(pc) {
            var order    = this.pos.get_order();
            var lines    = order.get_orderlines();
            var self = this;
            // Add discount
            var discount = pc / 100.0 * order.get_selected_orderline().get_price_without_tax();
            main_discount = discount;
            if (!order.get_orderlines().length) {
                return;
            }
            order.get_selected_orderline().set_discount(pc);
            var main = true;
            // $('.summary .total .subentry_discount .value')[0].textContent = order.get_total_discount(main);
            
        },
    });

    screens.define_action_button({
        'name': 'DiscountAll',
        'widget': DiscountAll,
    });

    var Order = models.Order.prototype;
    var service_charge = 0.0 
    var tax_charge_value = 0.0
    models.Order = models.Order.extend({
        template:'Order',
        initialize: function(attr,options){
            this.service_charge_type = 0;
            this.service_charge_value = 0.0;
            this.tax_type = false;
            this.tax_charge_value = 0.0;
            Order.initialize.apply(this, arguments);
        },
        init_from_JSON: function(json) {
            Order.init_from_JSON.call(this, json);
            this.service_charge = json.service_charge;
            this.service_charge_value = json.service_charge_value;
            this.tax_type = json.tax_type;
            this.tax_charge_value = json.tax_charge_value
        },
        export_as_JSON: function() {
            var ret=Order.export_as_JSON.call(this);
            ret.service_charge = this.service_charge;
            ret.service_charge_value = this.get_service_charge();
            ret.tax_type = this.tax_type;
            ret.tax_charge_value = this.get_total_tax();
            return ret;
        },
        set_service_charge: function(service_charge){
            this.service_charge = service_charge;
            self.service_charge = service_charge
            this.trigger('change',this);
        },
        set_tax_charge: function(tax_charge){
            this.tax_charge_value = tax_charge;
            self.tax_charge_value = tax_charge;
            this.trigger('change',this);
        },
        get_service_charge: function(){
            var self = this;
            return self.service_charge
        },
        get_total_tax: function() {
            var self = this;
            return round_pr(self.tax_charge_value, this.pos.currency.rounding);
        },
    });




});
