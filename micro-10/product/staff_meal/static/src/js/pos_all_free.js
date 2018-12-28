odoo.define('staff_meal.pos_all_free', function (require) {
"use strict";
var models = require('point_of_sale.models');
var Model = require('web.DataModel');
var screens = require('point_of_sale.screens');
var utils = require('web.utils');
var round_di = utils.round_decimals;

var Orderline = models.Orderline.prototype;
var Order = models.Order.prototype;

var OrderWidget = screens.OrderWidget.prototype;
var round_pr = utils.round_precision;
// var floors = require('pos_restaurant.floors');


var PopupWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
var gui = require('point_of_sale.gui');
var _t  = require('web.core')._t;
var SuperPosModel = models.PosModel.prototype;


var ConfirmationOptionPopupWidget = PopupWidget.extend({
    template: 'ConfirmationOptionPopupWidget',
     events: _.extend({}, PopupWidget.prototype.events, {
         'click .pin_number_button':  'toggle_button_pin',
         'click .email_button':  'toggle_button_email',
         'click .sms_button':  'toggle_button_sms',
         'click .button.next_func':  'next_func',
    }),
    toggle_button_pin : function () {
        this.$el.find('.row.email_button button').removeClass('active btn-fill');
        this.$el.find('.row.sms_button button').removeClass('active btn-fill');
        this.$el.find('.row.pin_number_button button').toggleClass('active btn-fill');

    },
    toggle_button_email : function () {
        this.$el.find('.row.email_button button').toggleClass('active btn-fill');
        this.$el.find('.row.sms_button button').removeClass('active btn-fill');
        this.$el.find('.row.pin_number_button button').removeClass('active btn-fill');

    },
    toggle_button_sms : function () {
        this.$el.find('.row.sms_button button').toggleClass('active btn-fill');
        this.$el.find('.row.email_button button').removeClass('active btn-fill');
        this.$el.find('.row.pin_number_button button').removeClass('active btn-fill');

    },
    next_func:function () {
        let email_active = this.$el.find('.row.email_button button').hasClass('active btn-fill');
        let sms_active = this.$el.find('.row.sms_button button').hasClass('active btn-fill');
        let pin_active = this.$el.find('.row.pin_number_button button').hasClass('active btn-fill');
        if(email_active){
            this.click_email_button();
        }
        if(sms_active){
            this.click_sms_button();
        }
        if(pin_active){
            this.click_pin_number_button();
        }
    },


    click_pin_number_button: function(){
        var self = this;
        this.gui.show_popup('number', {
            'title':  _t('Enter PIN Number'),
            'cheap': true,
            'value': '',
            'confirm': function(value) {
                var pin = value;
                if(!pin.trim()){
                    alert('Please Enter PIN First!');
                    return false
                }
                else{
                    var model = new Model('res.users');
                    model.call("compare_pin_number", [pin]).then(function (result) {
                            if (result){
                                self.gui.show_screen('payment');

                                // add paymentline
                                var order = self.pos.get_order();
                                order.add_staff_meal_paymentline();


                                $('.payment-numpad button.number-char').prop('disabled', true);
                                $('.payment-numpad button.numpad-char').prop('disabled', true);
                                $('.payment-numpad button.mode-button').prop('disabled', true);
                                $('.payment-numpad button.numpad-backspace').prop('disabled', true);
                                $('.paymentmethods').hide();
                                self.pos.get_order().all_free = true;
                                self.gui.current_screen.$('.next').off().click(function(){
                                    if(self.pos.category == 'staff_meal'){
                                        $('button.send_kitchen').click();
                                    }
                                    self.gui.current_screen.validate_order();
                                    // self.gui.show_screen('products');
                                });
                            }
                            else{
                                self.gui.show_screen('products');
                                alert("You have entered a wrong PIN")
                            }
                    });
                }
            },
            'cancel': function(){
                 self.gui.show_screen('products');
                alert('cancel');
            }
        });
    },
    click_email_button: function(){
        var self = this;
        var model = new Model('res.users');
        var order = this.pos.get_order();
        order.add_staff_meal_paymentline();
        var order_callback = this.pos.push_order(order);
        //need add paymentline staff meal
        order_callback.then(function () {
            model.call("send_mail_pos_managers", [self.pos.get_order().note]).then(function (result) {
                if (result){
                    alert("Send Notification to all manager");
                    self.gui.show_screen('products');
                }
                else{
                    alert("Some problem")
                }
            });
        });
        // this.pos.gui.screen_instances.payment.$el.find(".next").click()

        // this.pos.push_order(self.pos.get_order(),{});
        // posmodel.db.add_order(posmodel.get_order())

    },
    click_sms_button: function(){
        var self = this;
        var model = new Model('res.users');
        var order = this.pos.get_order();
        order.add_staff_meal_paymentline();
        var order_callback = this.pos.push_order(order);
        //need add paymentline staff meal
        order_callback.then(function () {
            model.call("send_sms_pos_managers", [self.pos.get_order().note]).then(function (result) {
                if (result){
                    alert("Send SMS to all manager");
                    self.gui.show_screen('products');
                }
                else{
                    alert("Some problem")
                }
            });
        });
    },

});
gui.define_popup({name:'ConfirmationOption', widget: ConfirmationOptionPopupWidget});

models.load_models([{
    model: 'account.journal',
    fields: ['sequence_id', 'id'],
    domain: function(self){ return [['name', '=', 'Staff Meal']]; },
    loaded: function(self, data) {
        if(data && data[0]){
            self.db.journal_staff_meal = [data[0].id,data[0].sequence_id[1]];
        }
    },
}]);

var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        _super_posmodel.initialize.call(this, session, attributes);
        var is_staff_meal = false;
    },

});
models.load_fields('pos.order', ['note']);

var OptionsPopupWidget = OptionsPopupWidget.include({
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};
    },

    events: _.extend({}, OptionsPopupWidget.prototype.events, {
         'click .button.staff_meal':  'click_staff_meal',
    }),
    click_staff_meal: function(){
        this.gui.show_popup('staffmealoptionpopup', {
            'title': _t("LET'S GET STARTED"),
        });
    },
});


models.Orderline = models.Orderline.extend({
    set_unit_price_free: function(price){
        this.order.assert_editable();
        // this.price = round_di(0 || 0, this.pos.dp['Product Price']);
        this.trigger('change',this);
    },
    export_as_JSON: function() {
        var ret=Orderline.export_as_JSON.call(this);
        if(this.all_free){
            ret.all_free = this.all_free;
        }
        return ret;
    },
});
// var _paylineproto = models.Paymentline.prototype;
// models.Paymentline = models.Paymentline.extend({
//     export_as_JSON: function () {
//         var res = _paylineproto.export_as_JSON.apply(this, arguments);
//         console.log('res',res);
//         if(this.pos.category == 'staff_meal'){
//             res.account_id = null;
//             // res.statement_id = this.pos.db.staff_meal_bank_statement_id;
//         }
//         return res;
//     },
// });

models.Order = models.Order.extend({
    init_from_JSON: function(json) {
        Order.init_from_JSON.call(this, json);
        this.all_free = json.all_free;
        this.is_staff_meal = json.is_staff_meal;
        this.note = json.note;

    },
    export_as_JSON: function() {
        var ret=Order.export_as_JSON.call(this);
        ret.all_free = this.all_free;
        ret.is_staff_meal = this.is_staff_meal;
        ret.note = this.note;
        return ret;
    },
    add_staff_meal_paymentline: function () {
        var self = this;
        var cashregister = Object.assign({}, self.pos.cashregisters[0]);
        cashregister.journal_id = self.pos.db.journal_staff_meal;
        this.add_paymentline( cashregister );
        this.paymentlines.models[this.paymentlines.length - 1].amount = this.get_total_with_tax();
        self.pos.gui.screen_instances.payment.reset_input();
        self.pos.gui.screen_instances.payment.render_paymentlines();
    },

    add_product: function(product, options){
        if(this.pos.all_free){
            this.pos.get_order().set_all_free(1);
        }
        Order.add_product.apply(this,arguments);
        if(this.pos.category == 'staff_meal'){
            var line = this.get_last_orderline();
            line.all_free = true;
        }
    },
    set_note:function(note){
        this.note = note;
        this.trigger('change',this);
    },
    set_all_free: function(all_free){
        this.all_free = all_free;
        this.trigger('change',this);
    },
    set_all_line_free : function(all_free){
        var all_lines = this.get_orderlines();
        for (var i = all_lines.length - 1; i >= 0; i--) {
            all_lines[i].trigger('change',all_lines[i]);
        }

    },
    set_all_price : function(all_free){
        this.set('all_free',all_free);
        var all_lines = this.get_orderlines();
        for (var i = all_lines.length - 1; i >= 0; i--) {
            all_lines[i].set_unit_price(all_lines[i].product.price)
        }

    },
    get_subtotal : function(){
        // if(this.all_free){return 0.0}
        if(this.receipt_free){return 0.0}
        return round_pr(this.orderlines.reduce((function(sum, orderLine){
            return sum + orderLine.get_display_price();
        }), 0), this.pos.currency.rounding);
    },
    get_total_with_tax: function() {
        // if(this.all_free){return 0.0}
        if(this.receipt_free){return 0.0}
        return this.get_total_without_tax() + this.get_total_tax();
    },
    get_total_without_tax: function() {
        // if(this.all_free){return 0.0};
        if(this.receipt_free){return 0.0}
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_without_tax();
        }), 0), this.pos.currency.rounding);
    },
});
var AllFreeOrderButton = screens.ActionButtonWidget.extend({
    template: 'AllFreeOrderButton',
    button_click: function() {
        var self = this;
        var order = this.pos.get_order();
        $('.all-free-button').toggleClass('all-free-on');
        if(!order.all_free){
            order.set_all_free(1);
            order.set_all_line_free()
            order.save_to_db();
        }
        else{
            order.set_all_free(0);
            order.set_all_price();
            order.save_to_db();
        }
    }
    });
  screens.define_action_button({
        'name': 'AllFreeOrderButton',
        'widget': AllFreeOrderButton
    });
  
screens.OrderWidget.include({
    renderElement: function(scrollbottom){
        this._super(scrollbottom);
        var order = this.pos.get_order();
        if(order && order.all_free){
            $('.all-free-button').addClass('all-free-on');
        }
        else{
            $('.all-free-button').removeClass('all-free-on');
        }
        
    },
  });   
screens.ProductScreenWidget.include({
        start: function(){ 
            var self = this;
            this._super();
            this.$('.control-buttons').find('.all-free-button').first().appendTo( this.$('.control-buttons').parent().find('.all-free-buttons-section')  );
            for(var i=0; i < this.$('.control-buttons').find('.all-free-button').length; i++){
                this.$('.control-buttons').find('.all-free-button').first().remove();
            }
            this.$('.control-buttons').parent().find('.all-free-buttons-section').addClass('control-buttons');
        },
        
    });

return {
    AllFreeOrderButton: AllFreeOrderButton,
    ConfirmationOptionPopupWidget: ConfirmationOptionPopupWidget,
    OptionsPopupWidget: OptionsPopupWidget,
}
});