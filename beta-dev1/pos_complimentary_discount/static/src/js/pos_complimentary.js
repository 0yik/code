odoo.define('pos_complimentary_discount.pos_complimentary', function (require) {
"use strict";

    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var floors = require('pos_restaurant.floors');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    
    var QWeb = core.qweb;
    var _t = core._t;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({      
        get_total_tax: function() {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                var tax = orderLine.get_complimentary() ? 0 : orderLine.get_tax();
                return sum + tax;
            }), 0), this.pos.currency.rounding);
        },
        get_total_without_tax: function() {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                var amount = orderLine.get_complimentary() ? 0 : orderLine.get_price_without_tax();
                return sum + amount;
            }), 0), this.pos.currency.rounding);
        },
   
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_complimentary: function(complimentary){
            this.is_complimentary = complimentary;
            this.trigger('change',this);
        },
        get_complimentary: function(complimentary){
            return this.is_complimentary;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_complimentary() !== this.get_complimentary()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.is_complimentary = this.is_complimentary;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.is_complimentary = this.is_complimentary;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.is_complimentary = json.is_complimentary;
        },
    });
    

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        process_complimentary_order: function(line, order){
            if(line.get_complimentary()){
                line.set_complimentary(false)
            }
            else{
                line.set_complimentary(true)
            }
            // line.set_dirty(false);
            // order.saveChanges();
        }
    });
    var complimentaryOrderButton = screens.ActionButtonWidget.extend({
        template: 'complimentaryOrderButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var line = this.pos.get_order().get_selected_orderline();

            if(!line){
                alert('There is no order line selected !');
                return;
            }
            else if(line){
                this.pos.process_complimentary_order(line,order);
            }
    	},
    });

    screens.define_action_button({
        'name': 'complimentaryOrderButton',
        'widget': complimentaryOrderButton
    });

});