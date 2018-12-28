odoo.define('pos_auto_discount', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        rerender_orderline: function (order_line) {
            try {
                this._super(order_line);
            } catch (e) {
                console.error(e);
            }
        }
    });
    models.load_models([
        {
            model: 'pos.auto.discount',
            fields: [],
            domain: function (self) {
                return [['state', '=', 'active']]
            },
            context: {'pos': true},
            loaded: function (self, discounts) {
                var discount_by_id = {};
                var discount_ids = [];
                for (var i = 0; i < discounts.length; i++) {
                    for (var j = 0; j < self.config.discount_ids.length; j++) {
                        if (self.config.discount_ids[j] == discounts[i].id) {
                            discount_by_id[discounts[i].id] = discounts[i];
                            discount_ids.push(discounts[i].id)
                        }
                    }
                }
                self.discount_by_id = discount_by_id;
                self.discount_ids = discount_ids;
            },
        }, {
            model: 'pos.auto.discount.rule',
            fields: [],
            domain: function (self) {
                return [['state', '=', 'active'], ['discount_id', 'in', self.discount_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discount_rules) {
                self.discount_rules_by_product_id = {};
                for (var x = 0; x < discount_rules.length; x++) {
                    var rule = discount_rules[x];
                    if (!self.discount_rules_by_product_id[self.discount_by_id[rule.discount_id[0]].product_id[0]]) {
                        self.discount_rules_by_product_id[self.discount_by_id[rule.discount_id[0]].product_id[0]] = [rule];
                    } else {
                        self.discount_rules_by_product_id[self.discount_by_id[rule.discount_id[0]].product_id[0]].push(rule);
                    }
                }
                console.log('END loading Discount rule.')
            },
        },
    ]);
    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        init_from_JSON: function (json) {
            _super_order_line.init_from_JSON.apply(this, arguments);
            if (json.discount_apply) {
                this.discount_apply = json.discount_apply;
            }
        },
        export_as_JSON: function () {
            var json = _super_order_line.export_as_JSON.apply(this, arguments);
            if (this.discount_apply) {
                json.discount_apply = this.discount_apply;
            }
            return json;
        },
        set_quantity: function (quantity) {
            var res = _super_order_line.set_quantity.apply(this, arguments);
            if (this.order && this.pos.discount_rules_by_product_id[this.product.id]) {
                this.checking_and_apply_discount();
            }
            return res
        },
        checking_and_apply_discount: function () {
            var order_lines = this.order.orderlines.models;
            var count_qty_by_product = this.quantity;
            var lines_will_update_price = [];
            for (var x = 0; x < order_lines.length; x++) {
                var line = order_lines[x];
                if (line.product.id == this.product.id && this.id != line.id) {
                    count_qty_by_product += line.quantity;
                    lines_will_update_price.push(line)
                }
            }
            for (var x in this.pos.discount_rules_by_product_id) {
                if (this.product.id == x) {
                    var rules = this.pos.discount_rules_by_product_id[x]
                    var rule_temp = null;
                    var qty_temp = 0;
                    for (var i=0; i < rules.length; i ++) {
                        var rule = rules[i];
                        if (count_qty_by_product >= rule.quantity && rule.quantity >= qty_temp) {
                            qty_temp = rule.quantity;
                            rule_temp = rule;
                        }
                    }
                    if (rule_temp) {
                        this.set_unit_price(rule_temp.list_price);
                    }
                }
            }
        }
    });

});