odoo.define('pos_pin_pizza.pin_number', function (require) {
"use strict";
var PopupWidget = require('point_of_sale.popups');
var PosUsernameWidget = require('point_of_sale.chrome');
var PosTableWidget = require('pos_restaurant.floors');
var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
var gui = require('point_of_sale.gui');
var ajax = require('web.ajax');
var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;


var NumberPopupWidget = PopupWidget.extend({
    template: 'NumberPopupWidget',
    show: function(options){
        options = options || {};
        this._super(options);

        this.inputbuffer = '' + (options.value   || '');
        this.decimal_separator = _t.database.parameters.decimal_point;
        this.renderElement();
        this.firstinput = true;
    },
    click_numpad: function(event){
        var newbuf = this.gui.numpad_input(
            this.inputbuffer, 
            $(event.target).data('action'), 
            {'firstinput': this.firstinput});

        this.firstinput = (newbuf.length === 0);

        if (newbuf !== this.inputbuffer) {
            this.inputbuffer = newbuf;
            this.$('.value').text(this.inputbuffer);
        }
    },
    click_confirm: function(){
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,this.inputbuffer);
        }
    },
});

OptionsPopupWidget.include({
    events: _.extend({}, OptionsPopupWidget.prototype.events, {
            'click .button.dive_in': 'dive_in_order_category',
        }),
    enter_pin_number: function (category) {
        var self = this;
        this.gui.show_popup('number', {
            'title':  _t('Enter PIN Number'),
            'cheap': true,
            'value': '',
            'confirm': function(value) {
                self.check_pin_number(category, value);
            },
            'cancel': function(){
                 self.gui.show_popup('optionpopup', {
                    'title': "LET'S GET STARTED",
                });
            }
        });
    },
    check_pin_number: function(category, value){
        var model = new Model('res.users');
        var user_id = this.pos.user.id;
        var self = this;
        model.call("read", [[user_id], ['pin_number']]).then(function (result) {
            if(result.length > 0 && result[0].pin_number == value){
                self.show_screen(category);
            }
            else{
                alert("Incorrect PIN number");
                self.gui.show_popup('optionpopup', {
                    'title': "LET'S GET STARTED",
                });
            }
        })
    },
    show_screen: function (category) {
        if(category == 'delivery'){
            this.show_screen_delivery();
        }
        if(category == 'dine_in'){
            this.show_screen_dinein();
        }
        if(category == 'take_away'){
            this.show_screen_take_away();
        }
        if(category == 'staff_meal'){
            this.show_screen_staff_meal();
        }
    },
    show_screen_delivery: function () {
        console.log("Delivery mode");
        this.pos.popup_option = 'Delivery'
        this.pos.category = 'delivery';
        var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
        if(this.pos.category != 'dive_in' && $CreateSalesOrderbutton){
            $CreateSalesOrderbutton.removeClass('oe_hidden');
        }
        this.gui.show_popup('deliveryoptionpopup', {
            'title': _t("LET'S GET STARTED"),
        });
    },
    show_screen_dinein: function () {
        var self = this.pos;
        $('.assign-order').removeClass('oe_hidden');
        this.pos.category = "dive_in";
        self.popup_option = 'Dine In'
        // this.pos.category = "dive_in";
        this.pos.all_free = false;
        this.pos.is_staff_meal = false;
        this.pos.dine_is_assign_order = false;
        // Fix: To show where it comes from In KDS screen
        var def = new $.Deferred();
        var fields = _.find(this.pos.models,function(model){
            return model.model === 'product.product';
        }).fields;
        var model = new Model('pos.order.category');
        // self.db.product_by_id = {};
        self.db.product_by_category_id = {};
        $('button.take_away_dinein').removeClass('oe_hidden');
        var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
        if(this.pos.category == 'dive_in' && $CreateSalesOrderbutton){
            $CreateSalesOrderbutton.addClass('oe_hidden');
        }
        model.call("get_current_category", ['Dine In',fields,this.pos.pricelist.id]).then(function (result) {
            if (result != 0){
                if (result == 1){
                    self.gui.screen_instances['products'].product_list_widget.product_list = [];
                    self.db.add_products([]);
                }else{
                    self.db.add_products(result);
                    self.gui.screen_instances['products'].product_list_widget.set_product_list(result);
                    self.gui.screen_instances['products'].product_list_widget.renderElement();
                }
            }else{
                alert("Wrong Product Order Category Defined")
            }
        });
        if (!self.config.iface_floorplan ||  self.floors.length == 0 ) {
            self.floors = []
            // self.floors_by_id = {};

            for (var i = 1; i <= Object.keys(self.floors_all_by_id ? self.floors_all_by_id : []).length ; i++) {
                if (self.floors_all_by_id[i].id == self.config.floor_ids[0]){
                    self.floors.push(self.floors_all_by_id[i])
                }

                self.floors_by_id[self.floors_all_by_id[i].id] = self.floors_all_by_id[i];
            }
            if(self.floors && self.floors.length>0 && !self.floors[0].tables.length ){
                self.floors[0].tables = []
                for(var i=0; i< Object.keys(self.floors[0].table_ids).length ; i++)
                {
                    self.floors[0].tables.push(self.tables_by_id[ self.floors[0].table_ids[i] ])
                }
            }
            self.config.iface_floorplan = 1;
            self.iface_floorplan = 1;
            this.gui.set_startup_screen('floors');
            this.gui.show_screen('floors');
            self.trigger('update:floor-screen');
        }
        else{
            this.gui.show_screen('floors');
        }
    },
    show_screen_take_away: function () {
        var self = this.pos;
        // Fix: To show where it comes from In KDS screen
        self.popup_option = 'Take Away'
        this.pos.category = "take_away";
        var floors = self.floors;
        self.floors_for_temp = floors;
        self.floors = [];
        self.floors_by_id = {};
        for (var i = 0; i < floors.length; i++) {
            floors[i].tables = [];
            self.floors_by_id[floors[i].id] = floors[i];
        }
        self.config.iface_floorplan = 0
        self.floors_for_temp = self.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });
        for (var i = self.floors_for_temp.length - 1; i >= 0; i--) {
            var floor = self.floors_for_temp[i]
            for (var j = floor.tables.length - 1; j >= 0; j--) {
                var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                tables.push([floor.tables[j]['id'],  table_name])
            }
        }
        this.pos.iface_floorplan = 0
        this.pos.add_new_order();

        var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
        if(this.pos.category != 'dive_in' && $CreateSalesOrderbutton){
            $CreateSalesOrderbutton.removeClass('oe_hidden');
        }
        //redirect to product screen
        this.gui.show_screen('clientlist');
        var def = new $.Deferred();
        var fields = _.find(this.pos.models,function(model){
            return model.model === 'product.product';
        }).fields;
        var model = new Model('pos.order.category');
        self.db.product_by_id = {};
        self.db.product_by_category_id = {};
        model.call("get_current_category", ['Take Away',fields,this.pos.pricelist.id]).then(function (result) {
            console.log('Get Catefory..Take Away..',result );
            if (result != 0){
                if (result == 1){
                    self.gui.screen_instances['products'].product_list_widget.product_list = [];
                    self.gui.screen_instances['products'].product_list_widget.renderElement();
                    self.db.add_products([]);
                }else{
                    self.db.add_products(result);
                    self.gui.screen_instances['products'].product_list_widget.product_list = result;
                    self.gui.screen_instances['products'].product_list_widget.renderElement();

                }
            }else{
                alert("Wrong Product Order Category Defined")
            }
        });
    },
    show_screen_staff_meal: function () {
        this.gui.show_popup('staffmealoptionpopup', {
            'title': _t("LET'S GET STARTED"),
        });
    },
    click_staff_meal: function(){
        this.enter_pin_number("staff_meal");
    },
    dislay_delivery_popup: function(){
        this.enter_pin_number("delivery");
    },
    dive_in_order_category: function(){
        try{
            this.enter_pin_number("dine_in");
        }catch (error) {
            console.log(error)
        }
    },
    click_take_away: function(){
        this.enter_pin_number("take_away");
    },
});
    PosUsernameWidget.UsernameWidget.include({
        click_username: function(){
        var self = this;
        /*this.gui.select_user({
            'security':     true,
            'current_user': this.pos.get_cashier(),
            'title':      _t('Change Cashier'),
        }).then(function(user){
            self.pos.set_cashier(user);
            self.renderElement();
        });*/
    },
});
});
