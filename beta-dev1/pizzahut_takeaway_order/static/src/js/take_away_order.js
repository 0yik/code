odoo.define('pizzahut_takeaway_order.takeaway_or1der', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
var gui = require('point_of_sale.gui');
var Model = require('web.DataModel');
var _t  = require('web.core')._t;

screens.PaymentScreenWidget.include({
    // Check if the order is paid, then sends it to the backend,
    // and complete the sale process
    validate_order: function(force_validation) {
        if (this.order_is_valid(force_validation)) {
            //added order button function to validate button.
            var order = this.pos.get_order();
            if(order.hasChangesToPrint()){
                order.printChanges();
                order.saveChanges();
            }
            this.finalize_validation();
        }
    },
});

OptionsPopupWidget.include({
    events: _.extend({}, OptionsPopupWidget.prototype.events, {
         'click .button.take_away': 'click_take_away',
    }),

    /* function called when a
    take away order option is selected
    it will redirect user to product screen
    */
    click_take_away: function(){
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
});

screens.OrderWidget.include({
    custom_view_take_away: function(){
        $('.seat_number_from_takeaway').hide();
        $('.order-submit').hide();
        $('.transfer-button').hide();
        $('.guest-button').hide();
        $('.CreateSalesOrderbutton').hide();
    },
    update_summary: function() {
        this._super();
        if(this.pos.category == 'take_away'){
            this.custom_view_take_away();
        }
    }
});

screens.ProductScreenWidget.include({
    show: function(){
        this._super();
        if(this.pos.category == 'take_away'){
            $('div.seat_number_from_takeaway').addClass('oe_hidden');
        }
    }
});

});

