odoo.define('staff_meal.staff_meal_option', function (require) {
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
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    var _t  = require('web.core')._t;

    var _super_posmodel = models.PosModel.prototype;
    var StaffMeanOptionsPopupWidget = PopupWidget.extend({
        template: 'StaffMeanOptionsPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .staff_mean_order_btn':  'staff_mean_order_click',
            'click .staff_mean_confirm_email_btn':  'staff_mean_confirm_email_click',
            'click .staff_mean_back': 'staff_mean_back',
        }),
        staff_mean_order_click : function () {

            this.category = "staff_meal";
            var current_pos = this.pos;
            var self = this;
            _super_posmodel.models.is_staff_meal = true;
            self.pos.all_free = true;
            var floors = current_pos.floors;
            current_pos.floors_for_temp = floors;
            current_pos.floors = [];
            current_pos.floors_by_id = {};
            current_pos.popup_option = 'Staff Meal';
            for (var i = 0; i < floors.length; i++) {
            floors[i].tables = [];
            current_pos.floors_by_id[floors[i].id] = floors[i];
            }
            current_pos.config.iface_floorplan = 0;
            current_pos.floors_for_temp = current_pos.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });

            for (var i = current_pos.floors_for_temp.length - 1; i >= 0; i--) {
            var floor = current_pos.floors_for_temp[i];
            for (var j = floor.tables.length - 1; j >= 0; j--) {
                var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                tables.push([floor.tables[j]['id'],  table_name]);
            }
            }
            this.pos.category = 'staff_meal';
            this.pos.iface_floorplan = 0
            this.pos.add_new_order();
            this.pos.all_free = true;
            this.pos.is_staff_meal = true;

            var order = this.pos;

            this.gui.show_screen('products');
            var fields = _.find(this.pos.models,function(model){
            return model.model === 'product.product';
            }).fields;
            // var model = new Model('pos.order.category');
            // current_pos.db.product_by_id = {};
            // current_pos.db.product_by_category_id = {};
            // model.call("get_current_category", ['Staff Meal',fields,this.pos.pricelist.id]).then(function (result) {
            // if (result != 0){
            //     if (result == 1){
            //         current_pos.gui.screen_instances['products'].product_list_widget.product_list = [];
            //         current_pos.db.add_products([]);
            //     }else{
            //         current_pos.db.add_products(result);
            //         current_pos.gui.screen_instances['products'].product_list_widget.set_product_list(result);
            //         current_pos.gui.screen_instances['products'].product_list_widget.renderElement();
            //     }
            // }else{
            //     alert("Wrong Product Order Category Defined")
            // }
            // });

            var order_reality = this.pos.get_order();
            order_reality.all_free = true;

            $('.pay').off().click(function(){
                var order = self.pos.get_order();
                if(order.category == 'staff_meal'){
                    order.all_free = true;
                    var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                        return line.has_valid_product_lot();
                    });
                    if(!has_valid_product_lot){
                        self.gui.show_popup('confirm',{
                            'title': _t('Empty Serial/Lot Number'),
                            'body':  _t('One or more product(s) required serial/lot number.'),
                            confirm: function(){
                                //self.gui.show_screen('payment');
                            },
                        });
                    }else{
                        //self.gui.show_screen('payment');
                    }
                    var note = prompt('Please fill the note.');
                    if(note != null){
                        order.note = note;
                        self.gui.show_popup('ConfirmationOption', {
                            'title': _t("Confirmation Option"),
                        });
                    }
                }

            });
        },
        staff_mean_confirm_email_click : function () {
            this.gui.show_screen('listpayment');
        },
        staff_mean_back:function () {
            var self = this;
            this.gui.show_popup('optionpopup', {
                'title': _t("LET'S GET STARTED"),
            });
            self.gui.screen_instances.products.$('.pay').off().click(function(){
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
        }

    });
    gui.define_popup({name:'staffmealoptionpopup', widget: StaffMeanOptionsPopupWidget});

    var GoToBackStaffMeal = screens.ActionButtonWidget.extend({
        template: 'GoToBackStaffMeal',
        button_click: function() {
            this.pos.gui.show_popup('staffmealoptionpopup', {
                'title': "LET'S GET STARTED",
            });
        },
    });
    screens.define_action_button({
        'name': 'GoToBackStaffMeal',
        'widget': GoToBackStaffMeal,
        'condition': function() {
            return true;
        },
    });

    screens.ProductScreenWidget.include({
        custom_view_delivery: function(){
            $('button.pay').attr("disabled", "disabled");
            $('button.back_delivery_btn').removeClass('oe_hidden');
            $('button.branch_btn').show();
            $('button.order-submit').hide();
            $('button.guest-button').hide();
            $('button.transfer-button').hide();
            $('div.seat_number_from_takeaway').hide();
            $('div.actionpad button.pay').hide();
            $('button.go-back-staff-meal').hide();
        },
        custom_view_staff_meal: function(){
            $('button.pay').removeAttr('disabled');
            $('button.pay').removeAttr('disabled');
            $('button.go-back-staff-meal').show();
            $('div.actionpad button.pay').removeClass('oe_hidden').show();
            $('.seat_number_from_takeaway').hide();
            $('.btn-newnote').hide();
            $('button.control-button:contains("Transfer")').hide();
            $('button.control-button:contains("Guests")').hide();
            $('button.control-button:contains("Note")').hide();
            $('div.control-button:contains("Rewards")').hide();
            $('.control-button:contains("All Orders")').hide();
            $('button.branch_btn').hide();
            $('button.back_delivery_btn').hide();
        },
        custom_general_view: function(){
            $('button.pay').removeAttr('disabled');
            $('button.pay').removeAttr('disabled');
            $('button.back_delivery_btn').addClass('oe_hidden');
            $('div.actionpad button.pay').removeClass('oe_hidden');
            $('button.order-submit').hide();
            $('button.guest-button').show();
            $('button.transfer-button').show();
            $('div.seat_number_from_takeaway').show();
            $('button.pay').show();
            $('button.go-back-staff-meal').show();
            $('button.branch_btn').hide();
        },
        custom_dine_in_view: function () {
            $('button.pay').removeAttr('disabled');
            $('button.pay').removeAttr('disabled');
            $('button.back_delivery_btn').addClass('oe_hidden');
            $('div.actionpad button.pay').removeClass('oe_hidden');
            $('button.order-submit').show();
            $('button.guest-button').show();
            $('button.transfer-button').show();
            $('div.seat_number_from_takeaway').show();
            $('button.pay').show();
            $('button.go-back-staff-meal').hide();
            $('button.branch_btn').hide();
        },
		show: function(){
			this._super();
			if(this.pos.category == 'staff_meal'){
                this.custom_view_staff_meal();
            }else if (this.pos.category == 'delivery') {
                this.custom_view_delivery();
            }else if(this.pos.category == "dine_in"){
			    this.custom_dine_in_view();
            }else {
                this.custom_general_view();
            }
		}
	});
    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            Order.add_product.call(this, product, options);
            if(this.pos.category == 'staff_meal') {
                $('.seat_number_from_takeaway').hide();
                $('.btn-newnote').hide();
                $('button.control-button:contains("Transfer")').hide();
                $('button.control-button:contains("Guests")').hide();
                $('button.control-button:contains("Note")').hide();
                $('div.control-button:contains("Rewards")').hide();
                $('.control-button:contains("All Orders")').hide();
                $('button.branch_btn').hide();
                $('button.back_delivery_btn').hide();
            }
        },
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity) {
            _super_orderline.set_quantity.apply(this, arguments);
            if(this.pos.category == 'staff_meal') {
                $('.seat_number_from_takeaway').hide();
                $('.btn-newnote').hide();
                $('button.control-button:contains("Transfer")').hide();
                $('button.control-button:contains("Guests")').hide();
                $('button.control-button:contains("Note")').hide();
                $('div.control-button:contains("Rewards")').hide();
                $('.control-button:contains("All Orders")').hide();
                $('button.branch_btn').hide();
                $('button.back_delivery_btn').hide();
            }
        }
    });

    return StaffMeanOptionsPopupWidget;
});