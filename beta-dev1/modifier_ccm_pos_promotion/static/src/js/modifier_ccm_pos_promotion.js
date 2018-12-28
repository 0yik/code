odoo.define('modifier_ccm_pos_promotion.modifier_ccm_pos_promotion', function(require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var models = require('point_of_sale.models');
require('pos_promotion');

var round_pr = utils.round_precision;

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    get_total_without_promotion_and_tax: function () {
        var rounding = this.pos.currency.rounding;
        var orderlines = this.orderlines.models
        var sum = 0
        var i = 0
        while (i < orderlines.length) {
            var line = orderlines[i];
            if (line.is_ordered) {
                sum += round_pr(line.get_unit_price() * line.get_quantity() * (1 - line.get_discount() / 100), rounding)
            }
            i++
        }
        return sum;
    },
    get_product_and_quantity_current_order: function () {
        var lines_list = {};
        var lines = this.orderlines.models;
        var i = 0;
        while (i < lines.length) {
            var line = lines[i];
            if (line.promotion || !line.is_ordered) {
                i++;
                continue
            }
            if (!lines_list[line.product.id]) {
                lines_list[line.product.id] = line.quantity;
            } else {
                lines_list[line.product.id] += line.quantity;
            }
            i++;
        }
        return lines_list
    },
    compute_discount_category: function (promotion) {
        var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
        if (!product || !this.pos.promotion_by_category_id) {
            return;
        }
        var lines = this.orderlines.models;
        if (lines.length) {
            var x = 0;
            while (x < lines.length) {
                if (lines[x].promotion_discount_category) {
                    this.remove_orderline(lines[x]);
                }
                x++;
            }
        }
        for (var i in this.pos.promotion_by_category_id) {
            var promotion_line = this.pos.promotion_by_category_id[i];
            var amount_total_by_category = 0;
            var z = 0;
            while (z < lines.length) {
                if (!lines[z].product.pos_categ_id || !lines[z].is_ordered) {
                    z++;
                    continue;
                }
                if (lines[z].product.pos_categ_id[0] == promotion_line.category_id[0]) {
                    amount_total_by_category += lines[z].get_price_without_tax();
                }
                z++;
            }
            if (amount_total_by_category > 0) {
                this.add_product(product, {
                    price: -amount_total_by_category / 100 * promotion_line.discount
                })
                var selected_line = this.get_selected_orderline();
                selected_line.promotion_discount_category = true;
                selected_line.promotion = true;
                selected_line.promotion_reason = ' discount ' + promotion_line.discount + ' % ' + promotion_line.category_id[1];
                selected_line.trigger('change', selected_line);
            }
        }
    },
});

});