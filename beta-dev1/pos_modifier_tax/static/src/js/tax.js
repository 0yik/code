odoo.define('pos_modifier_tax.pos_modifier_tax', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');

var TaxButton = screens.ActionButtonWidget.extend({
    template: 'TaxButton',
    button_click: function(){

        if (this.$el.data('mode') == 'tax'){
            this.$el.data('mode','no-tax')     
            this.$el[0].innerHTML = "Tax / <b>Non-Tax</b>"
        }
        else{
            this.$el.data('mode','tax')
            this.$el[0].innerHTML = "<b>Tax</b> / Non-Tax" 
        }
        
        
        var order = this.pos.get('selectedOrder')
        _.each(order.orderlines.models, function(line) {
            order.pos.gui.current_screen.order_widget.orderline_change(line);
        });

        
    },


});


models.Orderline = models.Orderline.extend({

    get_all_prices: function(){
        
        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            product_taxes.push(_.detect(taxes, function(t){
                return t.id === el;
            }));
        });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        if ($($.find('.tax_remove')[0]).data('mode') == 'tax'){

            return {
                "priceWithTax": all_taxes.total_included,
                "priceWithoutTax": all_taxes.total_excluded,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            }
        } else {
            return {
                "priceWithTax": all_taxes.total_excluded,
                "priceWithoutTax": all_taxes.total_excluded,
                "tax": 0,
                "taxDetails": {},
            }
        }
    },
});


screens.define_action_button({
    'name': 'Tax',
    'widget': TaxButton,
    
});


});
