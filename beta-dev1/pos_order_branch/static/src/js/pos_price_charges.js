odoo.define('pos_order_branch.pos_price_charges_calculation', function (require) {
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
             if(this.all_free){return 0.0};
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                var amount = orderLine.get_complimentary() ? 0 : orderLine.get_price_without_tax();
                return sum + amount;
            }), 0), this.pos.currency.rounding);
        },
        get_subtotal : function(){
            if(this.all_free){return 0.0}
            return round_pr(this.orderlines.reduce((function(sum, orderLine){
                return sum + orderLine.get_display_price();
            }), 0), this.pos.currency.rounding);
        },
        get_total_with_tax: function() {
            if(this.all_free){return 0.0}
            return this.get_total_without_tax() + this.get_total_tax();
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
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.call(this, json);
            this.service_charge = json.service_charge;
            this.service_charge_value = json.service_charge_value
            this.all_free = json.all_free;

        },
        export_as_JSON: function() {
            var ret=_super_order.export_as_JSON.call(this);
            ret.service_charge = this.service_charge;
            ret.service_charge_value = this.get_service_charge();
            ret.all_free = this.all_free;
            return ret;
        },
        set_service_charge: function(service_charge){
            this.service_charge = service_charge;
            this.trigger('change',this);
        },
        get_service_charge: function(){
            var service_charge = 0.0
            var orderlines = this.get_orderlines()
            for (var i = orderlines.length - 1; i >= 0; i--) {
                if(orderlines[i].service_charge_value){
                    service_charge += orderlines[i].get_service_charge()
                }
            }
            return service_charge
        },
        update_service_charge_lines: function(){
            var orderlines = this.get_orderlines()
            for (var i = orderlines.length - 1; i >= 0; i--) {
                orderlines[i].trigger('change', orderlines[i])
            }
        }
   
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            this.service_charge_type = false;
            this.service_charge_value = 0.0;
            if (options && options.product) {
                this.service_charge_type = options.product.service_charge_type;
                this.service_charge_value = options.product.service_charge_value;
            }
            _super_orderline.initialize.apply(this, arguments);
        },
        set_complimentary: function(complimentary){
            this.is_complimentary = complimentary;
            this.trigger('change',this);
        },
        get_complimentary: function(complimentary){
            return this.is_complimentary;
        },
        set_unit_price_free: function(price){
            this.order.assert_editable();
            this.price = round_di(0 || 0, this.pos.dp['Product Price']);
            this.trigger('change',this);
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
            json.service_charge_type = this.service_charge_type;
            json.service_charge_value = this.service_charge_value;
            
            if(this.order.all_free){
                json.price_unit = 0.0
            }
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.service_charge_type = json.service_charge_type;
            this.service_charge_value = json.service_charge_value;
            this.is_complimentary = json.is_complimentary;
        },
        set_service_charge_value: function(service_charge_value){
            // console.log('service_charge_value  '+service_charge_value)
            this.service_charge_value = service_charge_value
        },
        get_service_charge: function() {
            return this.service_charge_value;
        },
        compute_all: function(taxes, price_unit, quantity, currency_rounding, no_map_tax) {
            if (!this.is_complimentary && this.order.service_charge && this.product.service_charge_id.length > 0){
                var service_charge = this.order.pos.db.charge_tags[this.product.service_charge_id[0]]
            
                if (service_charge.service_charge_computation == 'fixed') {
                    price_unit += service_charge.amount;
                    // service_charge_value = service_charge.amount * quantity
                    this.set_service_charge_value(service_charge.amount * quantity)
                    // this.service_charge_value = service_charge.amount * quantity
                }
                if (service_charge.service_charge_computation == "percentage_of_price") {
                    var service_charge_value = (price_unit * service_charge.amount / 100)
                    price_unit += service_charge_value;
                    // service_charge_value = service_charge_value * quantity
                    // this.service_charge_value = service_charge_value * quantity
                    this.set_service_charge_value(service_charge_value * quantity)
                }
            }
            if(!this.order.service_charge || this.is_complimentary){
                this.set_service_charge_value(0.0)
                // this.service_charge_value = 0.0
            } 
            return _super_orderline.compute_all.call(this, taxes, price_unit, quantity, currency_rounding, no_map_tax);
        },
    });
    

    var ServiceChargeButton = screens.ActionButtonWidget.extend({
        template: 'ServiceChargeButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            $('.all-free-button').toggleClass('all-free-on');
            var order = this.pos.get_order();
            if(order.all_free && !order.service_charge){
                alert('When All Free is set, Service Charge can not be enabled.');
            }
            else{
                if(!order.service_charge){
                    order.set_service_charge(1);
                    order.update_service_charge_lines()
                    order.save_to_db();
                }
                else{
                    order.set_service_charge(0);
                    order.update_service_charge_lines()
                    order.save_to_db();
                }
            }
        }
    });

    models.load_fields('product.product', ['service_charge_id']);
    screens.define_action_button({
        'name': 'ServiceChargeButton',
        'widget': ServiceChargeButton,
    });

    screens.OrderWidget.include({
        renderElement: function(scrollbottom){
            this._super(scrollbottom);
            var order = this.pos.get_order();
            if(order && order.all_free){
                $('.all-free-button').addClass('all-free-on');
            }
            else{$('.all-free-button').removeClass('all-free-on')}

            if(order && order.service_charge){
                $('.service-charge-button').addClass('service-charge-on');
            }
            else{
            $('.service-charge-button').removeClass('service-charge-on')}
        },
        update_summary: function(){
            this._super();

            var order = this.pos.get_order();
            if (!order.get_orderlines().length) {
                return;
            }
            if(order.service_charge){
                var service_charge = order ? order.get_service_charge() : 0
                this.el.querySelector('.summary .total .subservice > .value').textContent = this.format_currency(service_charge);
                var taxes     = order ? total - order.get_total_without_tax() : 0;
                this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
            }else{
                this.el.querySelector('.summary .total .subservice > .value').textContent = this.format_currency(0.0);
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

    models.load_models({
        model: 'service.charge',
        fields: ['service_charge_computation','amount'],

        loaded: function(self, charge_tags){
            var ch_tags = {}
            for (var i = charge_tags.length - 1; i >= 0; i--) {
                ch_tags[charge_tags[i].id] = charge_tags[i]
            }
            self.db.charge_tags = ch_tags
        },
    });

    return {
        ServiceChargeButton: ServiceChargeButton,
    }
});