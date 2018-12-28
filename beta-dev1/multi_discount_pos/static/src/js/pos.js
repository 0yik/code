odoo.define('multi_discount_pos.pos', function (require) {
"use strict";
var core = require('web.core');
var Model = require('web.Model');
var utils = require('web.utils');
var models = require('point_of_sale.models');
var module = require('point_of_sale.screens');
var screens = require('point_of_sale.screens');

var _t = core._t;
var round_pr = utils.round_precision;
var PaymentScreenWidget = screens.PaymentScreenWidget;

// models.load_fields('res.partner', ['birth_date', 'is_birthdate_month']);
models.load_fields('pos.config',['multi_discount']);
models.load_fields('pos.order.line',['multi_discount','total_discount']);


var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    add_product: function(product, options){
        _super_order.add_product.apply(this,arguments);
        var order = this.pos.get('selectedOrder');
                var pos_config_b = new Model('pos.config');
                pos_config_b.query(['id','multi_discount'])
                            .filter([['id', '=', this.pos.pos_session.config_id[0]]])
                            .all().then(function(result){
                                order.orderlines.each(function(obj){
                                    obj.set_multi_discount(result[0].multi_discount);
                                });
                            });
            
        
        
    },
});

var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
        _super_orderline.initialize.apply(this,arguments);
        this.total_discount = 0;
        this.total_discount_str='';
    },
    clone: function(){
        _super_orderline.clone.apply(this,arguments);
        orderline.total_discount = this.total_discount;
        return orderline;
    },
    set_multi_discount: function(multi_discount){
        if (multi_discount!=""){
            var amount = 100;
            var splited_discounts = multi_discount.split("+");
            // if (',' in this.multi_discount){
            //      alert("You cannot use comma to separate discounts. Please add multiple discounts with '+' notation. \n For example 20 + 5.2");
            // }
            $.each(splited_discounts, function( index, value ) {
                var new_amount = (value * amount)/100;
                amount = (amount - new_amount);
            });
            this.total_discount = 100 - amount;
        }
        else{
            this.total_discount = 0;
        }
        // var member_disc_birth = Math.min(Math.max(parseFloat(birthday_discount) || 0, 0),100);
        // this.total_discount = ;
        this.total_discount_str = '' + this.total_discount;
        this.trigger('change', this);
    },

    get_multi_discount: function(){
        return this.total_discount;
    },
    get_multi_discount_str: function(){
        return this.total_discount_str;
    },
    get_base_price: function(){
        var rounding = this.pos.currency.rounding;
        var price_computed = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_multi_discount()/100), rounding);
        price_computed = round_pr(price_computed * (1 - this.get_discount()/100), rounding);
        return price_computed;
    },
    get_all_prices: function(){
        var base = round_pr( this.get_unit_price() * (1.0 - (this.get_multi_discount() / 100.0)), this.pos.currency.rounding);
        var price_unit_all = round_pr(base * (1.0 - (this.get_discount() / 100.0)), this.pos.currency.rounding);
        var price_unit = price_unit_all
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
        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
    },
    // init_from_JSON: function(json){
    //     _super_orderline.init_from_JSON.apply(this,arguments);
    //     this.set_multi_discount(json.total_discount);
    // },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.total_discount = this.get_multi_discount();
        return json;
    },
    export_for_printing: function() {
        var json = _super_orderline.export_for_printing.apply(this,arguments);
        json.total_discount = this.get_multi_discount();
        return json;
    },
});  

PaymentScreenWidget.include({
    start: function() {
        this._super();

        // move all order, today order and deposit button on top
        var pos_config_b = new Model('pos.config');
                pos_config_b.query(['id','multi_discount'])
                            .filter([['id', '=', this.pos.pos_session.config_id[0]]])
                            .all().then(function(result){
                                $(".disc").attr("disabled","disabled") ;
                                $('.disc').val(result[0].multi_discount);
                                if (result[0].multi_discount!=""){
                                    var amount = 100;
                                    var splited_discounts = result[0].multi_discount.split("+");
                                    // if (',' in this.multi_discount){
                                    //      alert("You cannot use comma to separate discounts. Please add multiple discounts with '+' notation. \n For example 20 + 5.2");
                                    // }
                                    $.each(splited_discounts, function( index, value ) {
                                        var new_amount = (value * amount)/100;
                                        amount = (amount - new_amount);
                                    });
                                    var tot_disc = 100 - amount;
                                    $(".tot_disc").attr("disabled","disabled") ;
                                    $('.tot_disc').val(tot_disc);
                                }
                                else{
                                    $('.tot_disc').val(0);
                                }
                            });
    },
});

// screens.ProductScreenWidget.include({
//     start: function(){
//             var self = this;
//             this._super();
//             this.PricelistWidget = new PricelistWidget(this,{});
//             this.PricelistWidget.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));
//             load_product = this.product_list_widget;
//         },
// });

});
