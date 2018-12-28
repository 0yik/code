odoo.define('pos_product_service_charge.pos_service_charge', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var db = require('point_of_sale.DB')


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
db = db.extend({

})

var Order = models.Order.prototype;

models.Order = models.Order.extend({
	template:'Order',
    init_from_JSON: function(json) {
        Order.init_from_JSON.call(this, json);
        this.service_charge = json.service_charge;
        this.service_charge_value = json.service_charge_value
    },
    export_as_JSON: function() {
        var ret=Order.export_as_JSON.call(this);
        ret.service_charge = this.service_charge;
        ret.service_charge_value = this.get_service_charge();
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

var OrderLine = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
	initialize: function(attr,options){
        this.service_charge_type = false;
        this.service_charge_value = 0.0;
        if (options && options.product) {
            this.service_charge_type = options.product.service_charge_type;
            this.service_charge_value = options.product.service_charge_value;
        }
        OrderLine.initialize.apply(this, arguments);
	},
	init_from_JSON: function(json) {
        this.service_charge_type = json.service_charge_type;
        this.service_charge_value = json.service_charge_value;
        OrderLine.init_from_JSON.apply(this, arguments);
	},
	export_as_JSON: function() {
	    var loaded = OrderLine.export_as_JSON.apply(this, arguments);
        loaded.service_charge_type = this.service_charge_type;
        loaded.service_charge_value = this.service_charge_value;
        return loaded;
	},
    set_service_charge_value: function(service_charge_value){
        // console.log('service_charge_value  '+service_charge_value)
        this.service_charge_value = service_charge_value
    },
    get_service_charge: function() {
        return this.service_charge_value;
    },
    compute_all: function(taxes, price_unit, quantity, currency_rounding, no_map_tax) {
        if (this.order.service_charge && this.product.service_charge_id.length > 0){
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
        if(!this.order.service_charge){
            this.set_service_charge_value(0.0)
            // this.service_charge_value = 0.0
        } 
        return OrderLine.compute_all.call(this, taxes, price_unit, quantity, currency_rounding, no_map_tax);
    },
});

screens.OrderWidget.include({
    renderElement: function(scrollbottom){
        this._super(scrollbottom);
        var order = this.pos.get_order();

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

var ServiceChargeButton = screens.ActionButtonWidget.extend({
    template: 'ServiceChargeButton',
    button_click: function() {
        var self = this;
        var order = this.pos.get_order();
        $('.service-charge-button').toggleClass('service-charge-on');
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
    });

models.load_fields('product.product', ['service_charge_id']);
    screens.define_action_button({
        'name': 'ServiceChargeButton',
        'widget': ServiceChargeButton,
    });
return ServiceChargeButton
});