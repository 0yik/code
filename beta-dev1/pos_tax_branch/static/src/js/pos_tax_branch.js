odoo.define('pos_tax_branch.pos_tax_branch', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    var Orderline = models.Orderline.prototype;
    var Order = models.Order.prototype;
    var gui = require('point_of_sale.gui');


    models.load_models([{
        model: 'res.branch',
        fields: ['id', 'name', 'telephone_no', '﻿address', 'company_id','tax_id'],
        loaded: function(self, branch) {
            self.res_branchs_by_id = {};
            branch.map(function (item) {
                self.res_branchs_by_id[item.id] = item;
            });
            var tax_id = self.res_branchs_by_id[self.config.branch_id[0]] ? self.res_branchs_by_id[self.config.branch_id[0]].tax_id[0] : false;
            self.branch_tax_id = self.taxes_by_id[tax_id];
        },
	}]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            var res = _super_order.initialize.apply(this, arguments);
            this.apply_tax = true;
            return res;
        },
        set_apply_tax : function (apply_tax) {
            this.apply_tax = apply_tax;
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

            product_taxes = this.order.apply_tax ? [this.pos.branch_tax_id] : [];

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
    });

    screens.OrderWidget.include({
        update_summary: function() {
            var order = this.pos.get_order();
            this._super();
            if (order.apply_tax){
                $('.control-button.button-tax').addClass('tax-apply');
            }else{
                $('.control-button.button-tax').removeClass('tax-apply');
            }
        }
    });

    var TaxButton = screens.ActionButtonWidget.extend({
        template: 'TaxButton',
        button_click: function() {
            var order = this.pos.get_order();
            order.set_apply_tax(!order.apply_tax);
            order.trigger('change',this);
        },
    });

    screens.define_action_button({
        'name': 'tax_button',
        'widget': TaxButton,
    });

});
