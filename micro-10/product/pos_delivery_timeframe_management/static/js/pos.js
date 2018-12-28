odoo.define('pos_delivery_timeframe_management.pos_delivery', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');

var _t = core._t;

var models = require('point_of_sale.models');
//Load timeframe data
models.load_models([
    {
        model: 'time.frame',
        fields: ['start', 'finish', 'price', 'qty',],
        loaded: function(self,result){
            if(result.length){
                //set time frame data in variable so that it can be fetched later using 
                //this.pos.get('timeframe');
                self.set('timeframe',result);
            }
        },
    }],{'after': 'product.product'});

var DeliveryCheckbox = screens.ActionButtonWidget.extend({
    template: 'TimeFrameDeliveryCheckbox',
    button_click: function(){
        var self = this;
        if ($('#apply_charges').prop('checked')) {
            var product_list = this.gui.screen_instances.products.product_list_widget.product_list

            for (var prod in product_list){
                if (product_list[prod].display_name == "Delivery Charges"){
                    product_list[prod].list_price == 50;
                    product_list[prod].lst_price == 50;
                    product_list[prod].price == 50;
                    self.pos.get_order().add_product(product_list[prod]);
                    order_lines = self.pos.get_order().orderlines.models
                    for (var line in order_lines){
                        if (order_lines[line].product.display_name == "Delivery Charges"){
                            //get timeframe objects
                            var time_frames = this.pos.get('timeframe')
                            var dt = new Date(); //get current date
                            var current_time = dt.getHours() //get current hour
                            for (var tf in time_frames){
                                if (current_time <= time_frames[tf].finish && current_time >= time_frames[tf].start){
                                    //set the price according to hours.
                                    order_lines[line].set_unit_price(0);
                                }
                            }
                        }
                    }
                }
            }
        }
        else{
            var order_lines = this.gui.pos.get_order().orderlines.models
            for (var line in order_lines){
                if (order_lines[line].product.display_name == "Delivery Charges"){
                    order_lines[line].set_quantity(0);
                }
            }
        }
    },
});

screens.define_action_button({
    'name': 'discount',
    'widget': DeliveryCheckbox,
    'condition': function(){
        return this.pos.config    },
    });
});
