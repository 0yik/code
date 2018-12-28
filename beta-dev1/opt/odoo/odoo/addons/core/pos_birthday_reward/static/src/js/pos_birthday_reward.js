odoo.define('pos_birthday_reward.pos_birthday_reward', function (require) {
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

models.load_fields('res.partner', ['birth_date', 'is_birthdate_month']);
models.load_fields('pos.config',['birthday_discount']);


var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    add_product: function(product, options){
        _super_order.add_product.apply(this,arguments);
        var order = this.pos.get('selectedOrder');
        if (order.get_client()){
            if(order.get_client().is_birthdate_month == true) {
                var pos_config_b = new Model('pos.config');
                pos_config_b.query(['id','birthday_discount'])
                            .filter([['id', '=', this.pos.pos_session.config_id[0]]])
                            .all().then(function(result){
                                order.orderlines.each(function(obj){
                                    obj.set_birthday_discount(result[0].birthday_discount);
                                });
                            });
            }
        }
        
    },
});

var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
        _super_orderline.initialize.apply(this,arguments);
        this.membership_birthmonth_discount = 0;
        this.member_birthmonth_discountStr = '';
    },
    clone: function(){
        _super_orderline.clone.apply(this,arguments);
        orderline.membership_birthmonth_discount = this.membership_birthmonth_discount;
        return orderline;
    },
    set_birthday_discount: function(birthday_discount){
        var member_disc_birth = Math.min(Math.max(parseFloat(birthday_discount) || 0, 0),100);
        this.membership_birthmonth_discount = member_disc_birth;
        this.member_birthmonth_discountStr = '' + member_disc_birth;
        this.trigger('change', this);
    },
    get_birthday_discount: function(){
        return this.membership_birthmonth_discount;
    },
    get_birthday_discount_str: function(){
        return this.member_birthmonth_discountStr;
    },
    get_base_price: function(){
        var rounding = this.pos.currency.rounding;
        var price_computed = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_birthday_discount()/100), rounding);
        price_computed = round_pr(price_computed * (1 - this.get_discount()/100), rounding);
        return price_computed;
    },
    get_all_prices: function(){
        var base = round_pr(this.get_quantity() * this.get_unit_price() * (1.0 - (this.get_birthday_discount() / 100.0)), this.pos.currency.rounding);
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
    init_from_JSON: function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        this.set_birthday_discount(json.membership_birthmonth_discount);
    },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.membership_birthmonth_discount = this.get_birthday_discount();
        return json;
    },
    export_for_printing: function() {
        var json = _super_orderline.export_for_printing.apply(this,arguments);
        json.membership_birthmonth_discount = this.get_birthday_discount();
        return json;
    },
});  

PaymentScreenWidget.include({
    customer_changed: function() {
        var self = this;
        var client = this.pos.get_client();
        this.$('.js_customer_name').text( client ? client.name : _t('Customer') );
        if(client){
            if(client.is_birthdate_month){
                    var order = this.pos.get('selectedOrder');

                if(order){
                 var a =  order.orderlines.each(function(obj){
                            
                            obj.set_birthday_discount(self.pos.config.birthday_discount);
                    });
                }
            }
            else{
                 var order = this.pos.get('selectedOrder');

                if(order){
                 var a =  order.orderlines.each(function(obj){
                            
                            obj.set_birthday_discount(0);
                    });
                }
            }
            
           
        }
    },

});

});
