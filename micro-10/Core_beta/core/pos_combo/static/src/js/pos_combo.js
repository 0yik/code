odoo.define('pos_combo', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Session = require('web.Session');
    var QWeb = core.qweb;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var _t = core._t;

    models.load_fields('product.product', 'pos_product_combo_ids');
    models.load_fields('product.product', 'pos_product_variant_ids');
    models.load_fields('product.product', 'pos_type');
    models.load_models([
        {
            model: 'pos.product.combo',
            fields: [],
            context: {},
            loaded: function (self, combo_list) {
                self.combos_by_product_id = {};
                for (var i = 0; i < combo_list.length; i++) {
                    var combo = combo_list[i];
                    if (!self.combos_by_product_id[combo.combo_id[0]]) {
                        self.combos_by_product_id[combo.combo_id[0]] = [combo];
                    } else {
                        self.combos_by_product_id[combo.combo_id[0]].push(combo);
                    }
                }
            }
        }, {
            model: 'pos.product.variant',
            fields: [],
            context: {},
            loaded: function (self, variants) {
                self.variants_by_product_id = {};
                self.variant_by_id = {};
                for (var i = 0; i < variants.length; i++) {
                    var variant = variants[i];
                    self.variant_by_id[variant.id] = variant;
                    if (!self.variants_by_product_id[variant.product_id[0]]) {
                        self.variants_by_product_id[variant.product_id[0]] = [variant];
                    } else {
                        self.variants_by_product_id[variant.product_id[0]].push(variant);
                    }
                }
            }
        }
    ]);

    var VariantPopup = PopupWidget.extend({
        template: 'VariantPopup',
        show: function (options) {
            var self = this;
            this._super(options);
            var variants = options.variants;
            var image_url = window.location.origin + '/web/image?model=product.product&field=image_medium&id=';
            self.$el.find('div.body').html(QWeb.render('VariantList', {
                variants: variants,
                image_url: image_url,
                widget: self
            }));
            self.pos.variants_selected = {};
            $('.product').click(function () {
                var variant_id = parseInt($(this).data('id'));
                var variant = self.pos.variant_by_id[variant_id];
                if (variant) {
                    if ($(this).closest('.product').hasClass("item-selected") == true) {
                        $(this).closest('.product').toggleClass("item-selected");
                        delete self.pos.variants_selected[variant.id];
                    } else {
                        $(this).closest('.product').toggleClass("item-selected");
                        self.pos.variants_selected[variant.id] = variant;

                    }
                }
            });
            $('.confirm-variant').click(function () {
                var variants_selected = self.pos.variants_selected;
                if (Object.keys(variants_selected).length == 0) {
                    console.log('You have not choice the product pack')
                } else {
                    var current_order = self.pos.get_order();
                    for (variant_index in variants_selected) {
                        var products = self.pos.db.product_by_id;
                        var product = products[variants_selected[variant_index].product_id[0]];
                        if (product) {
                            current_order.add_product(product, {
                                price: product.price + variants_selected[variant_index].price_extra,
                            })
                            var current_line = current_order.get_selected_orderline();
                            var variant = variants_selected[variant_index];
                            current_line.variant = variant;
                            var note = '';
                            if (variant.value_id1) {
                                note += variant.value_id1[1]
                            }
                            if (variant.value_id2) {
                                note += variant.value_id2[1]
                            }
                            if (variant.value_id3) {
                                note += variant.value_id3[1]
                            }
                            try {
                                current_line.set_note(note)
                            } catch (ex) {

                            }
                            current_line.trigger('change', current_line);
                        }
                    }
                }
            });
        }
    });
    gui.define_popup({name:'variants_popup', widget: VariantPopup});

    screens.ProductScreenWidget.include({
        click_product: function (product) {
            if (product.pos_type != 'multi_variant') {
                return this._super(product);
            } else {
                var variants = this.pos.variants_by_product_id[product.id]
                if (variants.length != 0) {
                    this.gui.show_popup('variants_popup', {
                        variants: variants
                    });
                } else {
                    this.pos.get_order().add_product(product);
                }
            }
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            var res = _super_order.add_product.apply(this, arguments);
            var last_orderline = this.get_last_orderline();
            if (last_orderline && last_orderline.id && (!this.pos.add_items_of_combo || this.pos.add_items_of_combo == false)) {
                last_orderline.clear_items_of_combo();
                last_orderline.add_items_of_combo(last_orderline.product, last_orderline.quantity);
            }
        },
    })

    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            var json = _super_order_line.export_as_JSON.apply(this,arguments);
            if (this.variant) {
                json.variant = this.variant;
            }
            if (this.combo) {
                json.combo = this.combo;
            }
            if (this.combo_of_line_id) {
                json.combo_of_line_id = this.combo_of_line_id;
            }
            if (this.product_combo) {
                json.product_combo = this.product_combo;
            }
            return json;
        },
        init_from_JSON: function(json) {
            _super_order_line.init_from_JSON.apply(this,arguments);
            if (json.variant) {
                this.variant = json.variant;
            }
            if (json.combo) {
                this.combo = json.combo;
            }
            if (json.combo_of_line_id) {
                this.combo_of_line_id = json.combo_of_line_id;
            }
            if (json.product_combo) {
                this.product_combo = json.product_combo;
            }
        },
        can_be_merged_with: function(orderline){
            if (orderline.combo || orderline.variant) {
                return false
            } else {
                return _super_order_line.can_be_merged_with.apply(this,arguments);
            }
        },
        export_for_printing: function(){
            var datas = _super_order_line.export_for_printing.apply(this, arguments);
            if (this.product_combo) {
                datas['product_combo'] = this.product_combo;
            }
            if (this.variant) {
                datas['variant'] = this.variant;
            }
            return datas;

        },
        set_quantity: function (quantity) {
            if (this.combo_of_line_id && quantity != 'remove') {
                return this.pos.gui.show_popup('error', _t('Combo item, you can not change anything'));
            } else {
                if (quantity != 'remove' && quantity != "") {
                    var res = _super_order_line.set_quantity.apply(this, arguments);
                    if (this.id) {
                        this.clear_items_of_combo();
                        this.add_items_of_combo(this.product, quantity);
                    }
                    return res;
                } else {
                    this.clear_items_of_combo();
                    return _super_order_line.set_quantity.apply(this, arguments);
                }

            }
        },
        set_unit_price: function (price) {
            if (this.combo_of_line_id) {
                return this.pos.gui.show_popup('error', _t('Combo item, you can not change anything'));
            } else {
                return _super_order_line.set_unit_price.apply(this, arguments);
            }
        },
        set_discount: function (discount) {
            if (this.combo_of_line_id) {
                this.pos.gui.show_popup('error', _t('Combo item, you can not change anything'));
            } else {
                return _super_order_line.set_discount.apply(this, arguments);
            }
        },
        clear_items_of_combo: function() {
            var items_of_combo = [];
            for (var x=0; x < this.order.orderlines.models.length; x ++) {
                var current_line = this.order.orderlines.models[x];
                if (current_line.id != this.id && current_line.combo_of_line_id && current_line.combo_of_line_id == this.id) {
                    items_of_combo.push(current_line)
                }
            }
            if (items_of_combo) {
                for (item in items_of_combo) {
                    this.order.remove_orderline(items_of_combo[item]);
                }
            }
        },
        add_items_of_combo: function(product, quantity) {
            this.pos.add_items_of_combo = true;
            var combo_list = this.pos.combos_by_product_id[product.id];
            if (combo_list) {
                for (combo_index_str_id in combo_list) {
                    var combo = combo_list[combo_index_str_id];
                    var products = this.pos.db.product_by_id;
                    var product_combo = products[combo.product_id[0]];
                    this.order.add_product(product_combo, {
                        price: 0,
                        quantity: combo.quantity * quantity,
                    })
                    var current_line = this.order.get_selected_orderline();
                    current_line.combo = combo;
                    current_line.combo_of_line_id = this.id;
                    current_line.product_combo = this.product.display_name;
                    current_line.trigger('change', current_line);

                }
            }
            this.pos.add_items_of_combo = false;
            return 1;
        }
    });
});
