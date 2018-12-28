odoo.define('pos_all_free.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var utils = require('web.utils');
var round_di = utils.round_decimals;

var Orderline = models.Orderline.prototype;
var Order = models.Order.prototype;

var OrderWidget = screens.OrderWidget.prototype;
var round_pr = utils.round_precision;

models.Orderline = models.Orderline.extend({
    set_unit_price_free: function(price){
        this.order.assert_editable();
        this.price = round_di(0 || 0, this.pos.dp['Product Price']);
        this.trigger('change',this);
    },
    export_as_JSON: function() {
        var ret=Orderline.export_as_JSON.call(this);
        if(this.order.all_free){
            ret.price_unit = 0.0
        }
        return ret;
    },
});

models.Order = models.Order.extend({
    init_from_JSON: function(json) {
        Order.init_from_JSON.call(this, json);
        this.all_free = json.all_free;
    },
    export_as_JSON: function() {
        var ret=Order.export_as_JSON.call(this);
        ret.all_free = this.all_free;
        return ret;
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
        if(this.all_free){return 0.0}
        return round_pr(this.orderlines.reduce((function(sum, orderLine){
            return sum + orderLine.get_display_price();
        }), 0), this.pos.currency.rounding);
    },
    get_total_with_tax: function() {
        if(this.all_free){return 0.0}
        return this.get_total_without_tax() + this.get_total_tax();
    },
    get_total_without_tax: function() {
        if(this.all_free){return 0.0};
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
        else{$('.all-free-button').removeClass('all-free-on')}
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
return AllFreeOrderButton

});