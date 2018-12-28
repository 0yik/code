odoo.define('pos_promotion_extension', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require("point_of_sale.popups");
    var Promotions = require("pos_promotion");
    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    models.load_models([
        {
            model: 'pos.promotion',
            fields: [],
            domain: function (self) {
                return [['id', 'in', self.config.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, promotions) {
                self.promotions = promotions;
                self.promotion_by_id = {};
                self.promotion_ids = []
                var i = 0;
                while (i < promotions.length) {
                    self.promotion_by_id[promotions[i].id] = promotions[i];
                    self.promotion_ids.push(promotions[i].id);
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.order',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts) {
                self.promotion_discount_order_by_id = {};
                self.promotion_discount_order_by_promotion_id = {};
                var i = 0;
                while (i < discounts.length) {
                    self.promotion_discount_order_by_id[discounts[i].id] = discounts[i];
                    if (!self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]]) {
                        self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]] = [discounts[i]]
                    } else {
                        self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]].push(discounts[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.category',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_category) {
                self.promotion_by_category_id = {};
                var i = 0;
                while (i < discounts_category.length) {
                    self.promotion_by_category_id[discounts_category[i].category_id[0]] = discounts_category[i];
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.quantity',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_quantity) {
                self.promotion_quantity_by_product_id = {};
                var i = 0;
                while (i < discounts_quantity.length) {
                    if (!self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]]) {
                        self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]] = [discounts_quantity[i]]
                    } else {
                        self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]].push(discounts_quantity[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.condition',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, gift_conditions) {
                self.promotion_gift_condition_by_promotion_id = {};
                var i = 0;
                while (i < gift_conditions.length) {
                    if (!self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]]) {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]] = [gift_conditions[i]]
                    } else {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]].push(gift_conditions[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.free',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, gifts_free) {
                self.promotion_gift_free_by_promotion_id = {};
                var i = 0;
                while (i < gifts_free.length) {
                    if (!self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]]) {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]] = [gifts_free[i]]
                    } else {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]].push(gifts_free[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.condition',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discount_conditions) {
                self.promotion_discount_condition_by_promotion_id = {};
                var i = 0;
                while (i < discount_conditions.length) {
                    if (!self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]]) {
                        self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]] = [discount_conditions[i]]
                    } else {
                        self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]].push(discount_conditions[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.apply',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_apply) {
                self.promotion_discount_apply_by_promotion_id = {};
                var i = 0;
                while (i < discounts_apply.length) {
                    if (!self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]]) {
                        self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]] = [discounts_apply[i]]
                    } else {
                        self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]].push(discounts_apply[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.price',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, prices) {
                self.promotion_price_by_promotion_id = {};
                var i = 0;
                while (i < prices.length) {
                    if (!self.promotion_price_by_promotion_id[prices[i].promotion_id[0]]) {
                        self.promotion_price_by_promotion_id[prices[i].promotion_id[0]] = [prices[i]]
                    } else {
                        self.promotion_price_by_promotion_id[prices[i].promotion_id[0]].push(prices[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.payment',
            fields: [],
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_payment) {
                self.promotion_discount_payment_promotion_id = {};
                var i = 0;
                while (i < discounts_payment.length) {
                    if (!self.promotion_discount_payment_promotion_id[discounts_payment[i].promotion_id[0]]) {
                        self.promotion_discount_payment_promotion_id[discounts_payment[i].promotion_id[0]] = [discounts_payment[i]]
                    } else {
                        self.promotion_discount_payment_promotion_id[discounts_payment[i].promotion_id[0]].push(discounts_payment[i])
                    }
                    i++;
                }
            }
        }
    ]);

    var _super_order = models.Order.prototype;
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        init_from_JSON: function (json) {
            if (json.promotion) {
                this.promotion = json.promotion;
            }
            if (json.promotion_reason) {
                this.promotion_reason = json.promotion_reason;
            }
            if (json.promotion_discount_total_order) {
                this.promotion_discount_total_order = json.promotion_discount_total_order;
            }
            if (json.promotion_discount_category) {
                this.promotion_discount_category = json.promotion_discount_category;
            }
            if (json.promotion_discount_by_quantity) {
                this.promotion_discount_by_quantity = json.promotion_discount_by_quantity;
            }
            if (json.promotion_gift) {
                this.promotion_gift = json.promotion_gift;
            }
            if (json.promotion_discount) {
                this.promotion_discount = json.promotion_discount;
            }
            if (json.promotion_price_by_quantity) {
                this.promotion_price_by_quantity = json.promotion_price_by_quantity;
            }
            if (json.promotion_discount_payment) {
                this.promotion_discount_payment = json.promotion_discount_payment;
            }
            return _super_orderline.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function () {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            if (this.promotion) {
                json.promotion = this.promotion;
            }
            if (this.promotion_reason) {
                json.promotion_reason = this.promotion_reason;
            }
            if (this.promotion_discount_total_order) {
                json.promotion_discount_total_order = this.promotion_discount_total_order;
            }
            if (this.promotion_discount_category) {
                json.promotion_discount_category = this.promotion_discount_category;
            }
            if (this.promotion_discount_by_quantity) {
                json.promotion_discount_by_quantity = this.promotion_discount_by_quantity;
            }
            if (this.promotion_gift) {
                json.promotion_gift = this.promotion_gift;
            }
            if (this.promotion_discount) {
                json.promotion_discount = this.promotion_discount;
            }
            if (this.promotion_price_by_quantity) {
                json.promotion_price_by_quantity = this.promotion_price_by_quantity;
            }
            if (this.promotion_discount_payment) {
                json.promotion_discount_payment = this.promotion_discount_payment;
            }
            return json;
        },
        export_for_printing: function () {
            var res = _super_orderline.export_for_printing.call(this);
            if (this.promotion) {
                res.promotion = this.promotion;
                res.promotion_reason = this.promotion_reason;
            }
            return res
        },
        can_be_merged_with: function (orderline) {
            _super_orderline.can_be_merged_with.apply(this, arguments);
            if (this.promotion) {
                return false;
            }
        },
    });
    var promotion_popup = PopupWidget.extend({
        template: 'promotion_popup',
        init: function (parent, options) {
            this._super(parent, options);
            this.promotions = this.pos.promotions;
        },
        renderElement: function () {
            var promotions_cache = this.pos.promotions;
            var promotions_show = [];
            var i = 0
            var order = this.pos.get_order();
            if (promotions_cache.length && order) {
                while (i < promotions_cache.length) {
                    var promotion = promotions_cache[i];
                    var type = promotion.type
                    if (type == '1_discount_total_order') {
                        var check = order.checking_apply_total_order(promotion);
                        if (check) {
                            promotions_show.push(promotion);
                        }
                    }
                    if (type == '2_discount_category') {
                        if (this.pos.promotion_by_category_id) {
                            promotions_show.push(promotion);
                        }
                    }
                    if (type == '3_discount_by_quantity_of_product' || type == '6_price_filter_quantity'|| type == '7_total_price_filter_quantity') {
                        promotions_show.push(promotion);
                    }
                    if (type == '4_pack_discount') {
                        var promotion_condition_items = order.pos.promotion_discount_condition_by_promotion_id[promotion.id];
                        var check = order.checking_can_apply_promotion(promotion_condition_items);
                        if (check == true) {
                            promotions_show.push(promotion);
                        }
                    }
                    if (type == '5_pack_free_gift') {
                        var promotion_condition_items = order.pos.promotion_gift_condition_by_promotion_id[promotion.id];
                        var check = order.checking_can_apply_promotion(promotion_condition_items);
                        if (check == true) {
                            promotions_show.push(promotion);
                        }

                    }
                    if (type == '8_payment_method_discount') {
                        promotions_show.push(promotion);
                    }
                    i++
                }
            }

            this.promotions = promotions_show;
            this._super();
            var self = this;
            $('.promotion-line').click(function () {
                var promotion_id = parseInt($(this).data()['id']);
                var promotion = self.pos.promotion_by_id[promotion_id];
                var type = promotion.type;
                var order = self.pos.get('selectedOrder');
                if (order.orderlines.length) {
                    if (type == '1_discount_total_order') {
                        order.compute_discount_total_order(promotion);
                    }
                    if (type == '2_discount_category') {
                        order.compute_discount_category(promotion);
                    }
                    if (type == '3_discount_by_quantity_of_product') {
                        order.compute_discount_by_quantity_of_products(promotion);
                    }
                    if (type == '4_pack_discount') {
                        order.compute_pack_discount(promotion);
                    }
                    if (type == '5_pack_free_gift') {
                        order.compute_pack_free_gift(promotion);
                    }
                    if (type == '6_price_filter_quantity') {
                        order.compute_price_filter_quantity(promotion);
                    }
                    if (type == '7_total_price_filter_quantity') {
                        order.compute_total_price_filter_quantity(promotion);
                    }
                    if (type == '8_payment_method_discount') {
                        order.compute_discount_payment(promotion);
                    }
                }
            })
            $('.remove_promotion').click(function () {
                var order = self.pos.get('selectedOrder');
                var lines = order.orderlines.models;
                var lines_remove = [];
                var i = 0;
                while (i < lines.length) {
                    var line = lines[i];
                    if (line.promotion && line.promotion == true) {
                        lines_remove.push(line)
                    }
                    i++;
                }
                order.remove_promotion_lines(lines_remove)
                order.trigger('change', order);
            })
        }
    })
    gui.define_popup({
        name: 'promotion_popup',
        widget: promotion_popup
    });
    models.Order = models.Order.extend({
        auto_build_promotion: function () {
            if (!this.pos.building_promotion || this.pos.building_promotion == false) {
                if (this.pos.config.allow_promotion == true && this.pos.config.promotion_ids.length) {
                    this.pos.building_promotion = true;
                    var promotions = this.pos.promotions
                    if (promotions) {
                        for (var i = 0; i < promotions.length; i++) {
                            var type = promotions[i].type
                            var order = this;
                            if (order.orderlines.length) {
                                if (type == '1_discount_total_order') {
                                    order.compute_discount_total_order(promotions[i]);
                                }
                                if (type == '2_discount_category') {
                                    order.compute_discount_category(promotions[i]);
                                }
                                if (type == '3_discount_by_quantity_of_product') {
                                    order.compute_discount_by_quantity_of_products(promotions[i]);
                                }
                                if (type == '4_pack_discount') {
                                    order.compute_pack_discount(promotions[i]);
                                }
                                if (type == '5_pack_free_gift') {
                                    order.compute_pack_free_gift(promotions[i]);
                                }
                                if (type == '6_price_filter_quantity') {
                                    order.compute_price_filter_quantity(promotions[i]);
                                }
                                if (type == '7_total_price_filter_quantity') {
                                    order.compute_total_price_filter_quantity(promotions[i]);
                                }
                                if (type == '8_payment_method_discount') {
                                    order.compute_discount_payment(promotions[i]);
                                }
                            }
                        }
                    }
                    this.pos.building_promotion = false;
                }
            }
        },
        compute_total_price_filter_quantity: function (promotion) {
            var promotion_prices = this.pos.promotion_price_by_promotion_id[promotion.id]
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            var i = 0;
            var lines = this.orderlines.models;
            var lines_remove = [];
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_price_by_quantity && line.promotion_price_by_quantity == true) {
                    lines_remove.push(line)
                }
                i++;
            }
            this.remove_promotion_lines(lines_remove);
            if (promotion_prices) {
                var prices_item_by_product_id = {};
                for (var i = 0; i < promotion_prices.length; i++) {
                    var item = promotion_prices[i];
                    if (!prices_item_by_product_id[item.product_id[0]]) {
                        prices_item_by_product_id[item.product_id[0]] = [item]
                    } else {
                        prices_item_by_product_id[item.product_id[0]].push(item)
                    }
                }
                var quantity_by_product_id = this.get_product_and_quantity_current_order()
                var discount = 0;
                for (i in quantity_by_product_id) {
                    if (prices_item_by_product_id[i]) {
                        var quantity_tmp = 0
                        var price_item_tmp = null
                        // root: quantity line, we'll compare this with 2 variable quantity line greater minimum quantity of item and greater quantity temp
                        for (var j = 0; j < prices_item_by_product_id[i].length; j++) {
                            var price_item = prices_item_by_product_id[i][j];
                            if (quantity_by_product_id[i] >= price_item.minimum_quantity && quantity_by_product_id[i] >= quantity_tmp) {
                                quantity_tmp = price_item.minimum_quantity;
                                price_item_tmp = price_item;
                            }
                        }
                        if (price_item_tmp) {
                            var discount = 0;
                            var z = 0;
                            var qty = 0;
                            while (z < lines.length) {
                                var line = lines[z];
                                if (line.product.id == price_item_tmp.product_id[0]) {
                                    discount += line.get_price_without_tax() - price_item_tmp.list_price
                                    qty = line.quantity;
                                }
                                z++;
                            }
                            var new_product = product;
                            // new_product.price = price_item_tmp.list_price/line.quantity;
                            // new_product.list_price = price_item_tmp.list_price/line.quantity;
                            if (discount > 0) {
                                this.add_product(new_product, {
                                    price: -discount,
                                })
                                var selected_line = this.get_selected_orderline();
                                selected_line.promotion_price_by_quantity = true;
                                selected_line.promotion = true;
                                selected_line.promotion_reason = ' By greater or equal ' + price_item_tmp.minimum_quantity + ' ' + selected_line.product.uom_id[1] + ' ' + price_item_tmp.product_id[1] + ' applied total price ' + price_item_tmp.list_price
                                selected_line.trigger('change', selected_line);
                            }
                        }
                    }
                }

            }
        },
        checking_discount_payment: function (promotion) {
            var discount_lines = this.pos.promotion_discount_payment_promotion_id[promotion.id];
            var total_order = this.get_total_without_promotion_and_tax();
            console.log('check_discount:',discount_lines);
            console.log("total_order:",total_order);
            var lines = this.orderlines.models;
            if (lines.length) {
                for (var j = 0; j < lines.length; j++) {
                    if (lines[j].promotion_discount_payment) {
                        this.remove_orderline(lines[j]);
                    }
                }
            }
            var discount_line_tmp = null;
            var discount_min_tmp = 0;
            var discount_max_tmp = 0;
            var discount_values = 0;
            if (discount_lines) {
                var i = 0;
                while (i < discount_lines.length) {
                    var discount_line = discount_lines[i];
                    if (total_order >= discount_line.min_amount && total_order >= discount_min_tmp) {
                        discount_line_tmp = discount_line;
                        discount_min_tmp = discount_line.min_amount
                    }
                    if (total_order <= discount_line.max_amount && total_order <= discount_max_tmp) {
                        discount_line_tmp = discount_line;
                        discount_max_tmp = discount_line.max_amount
                    }
                    if (discount_line.discount_value > 0 && discount_line.discount_value == discount_values) {
                        discount_line_tmp = discount_line;
                        discount_values = discount_line.discount_value
                    }
                    if (total_order )
                    i++;
                }
            }
            return discount_line_tmp;
        },
        compute_discount_payment: function (promotion) {
            var discount_line_tmp = this.checking_discount_payment(promotion)
            var total_order = this.get_total_without_promotion_and_tax();
            if (discount_line_tmp) {
            console.log("discount:",discount_line_tmp);
                var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                if (product) {
                    console.log("product:",product);
                    var discount = 0;
                    if ((total_order >= discount_line_tmp.min_amount) && (total_order <= discount_line_tmp.max_amount) && (discount_line_tmp.discount_value > 0)) {
                        discount = discount_line_tmp.discount_type == 'fixed_amount' ? -discount_line_tmp.discount_value : -total_order / 100 * discount_line_tmp.discount_value;
                        this.add_product(product, {
                            price: discount
                        })
                        var selected_line = this.get_selected_orderline();
                        var discount_value = discount_line_tmp.discount_type == 'percentage'?  discount_line_tmp.discount_value + ' % ': ' $ ' + discount_line_tmp.discount_value;
                        selected_line.promotion_discount_payment = true;
                        selected_line.promotion = true;
                        selected_line.promotion_reason = 'discount ' + discount_value + ' when total order are between ' +  discount_line_tmp.min_amount + ' and ' + discount_line_tmp.max_amount;
                        selected_line.trigger('change', selected_line);
                    }
                }
            }
        },
    })

});
