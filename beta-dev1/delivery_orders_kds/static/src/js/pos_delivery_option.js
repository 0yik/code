odoo.define('delivery_orders_kds.pos_delivery_option', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var PopupWidget = require('point_of_sale.popups');

    var DeliveryOptionsPopupWidget = PopupWidget.extend({
        template: 'DeliveryOptionsPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
             'click .order_option_btn':  'dislay_product_screen',
             'click .delivery_option_btn':  'dislay_delivery_list_screen',
             'click .payment_option_btn':  'dislay_payment_list_screen',
        }),
        click_cancel: function () {
            this.gui.show_popup('optionpopup', {
                'title': "LET'S GET STARTED",
            });
        },
        dislay_product_screen: function(){
            this.pos.popup_option = 'Delivery'
            this.pos.config.iface_floorplan = 0;
            this.pos.add_new_order();
            this.pos.get_order().branch_id = this.pos.get_branch() && this.pos.get_branch().id;
            this.gui.show_screen('products');
            this.gui.show_screen('clientlist');
            //this.get_current_category();
        },
        prepare_order: function () {
            var self = this.pos;
            self.popup_option = 'Delivery'
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
                console.log('TABLES',floor)
                for (var j = floor.tables.length - 1; j >= 0; j--) {
                    var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                    tables.push([floor.tables[j]['id'],  table_name])
                    console.log('TABLES',floor.tables[j])
                }
            }
        },
        get_current_category: function () {
            var self = this.pos;
            var def = new $.Deferred();
            var fields = _.find(this.pos.models,function(model){
                return model.model === 'product.product';
            }).fields;
            var model = new Model('pos.order.category');
            self.db.product_by_id = {};
            self.db.product_by_category_id = {};
            model.call("get_current_category", ['Delivery',fields,this.pos.pricelist.id]).then(function (result) {
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
        dislay_payment_list_screen: function(){
            var self = this.pos;
            this.gui.show_screen('invoicelist');
        },
        dislay_delivery_list_screen: function(){
            var self = this.pos;
            this.gui.show_screen('deliverylist');
        },
    });
    gui.define_popup({name:'deliveryoptionpopup', widget: DeliveryOptionsPopupWidget});

    return DeliveryOptionsPopupWidget;
});