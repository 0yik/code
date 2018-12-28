odoo.define("pos_screen_for_variants.pos_variants",function (require) {

    var core = require('web.core');
    var Model = require('web.DataModel');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var data = require('web.data');
    var chorme = require("point_of_sale.chrome");
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var load_product;

    var QWeb = core.qweb;
    var _t = core._t;
    var product_model = new Model('product.product');

    models.load_models([
        {
            model: 'product.template',
            domain: function(self) {
			return [
				['available_in_pos', '=', true]
			]; },
            fields: ['id', 'name', 'display_name', '﻿uom_id', 'default_code', 'list_price', 'product_variant_ids', 
                'product_variant_id', 'attribute_line_ids','categ_id'],
            loaded: function (self, products) {
                self.db.product_tmpl_ids = _.map(products, function (product) {
                    return product.id;
                });
                self.db.product_tmpls = {};
                _.map(products, function (product) {
                    return self.db.product_tmpls[product.id] = product;
                });
            },
        },
        {
            model: 'product.attribute.line',
            fields: ['id', 'display_name', 'product_tmpl_id', 'value_ids'],
            loaded: function (self, lines) {
                self.db.attribute_line_ids = _.map(lines, function (line) {
                    return line.id;
                });
                self.db.attribute_lines = {};
                _.map(lines, function (line) {
                    return self.db.attribute_lines[line.id] = line;
                });
            },
        },
        {
            model: 'product.attribute.value',
            fields: ['id', 'name', 'display_name', 'price_extra', 'product_ids', 'attribute_id'],
            loaded: function (self, values) {
                self.db.attribute_value_ids = _.map(values, function (value) {
                    return value.id;
                });
                self.db.attribute_values = {};
                _.map(values, function (value) {
                    return self.db.attribute_values[value.id] = value;
                });
            },
        }

    ]);

    screens.ProductListWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.product_tmpl_ids = this.pos.db.product_tmpl_ids;
            this.product_tmpls = this.pos.db.product_tmpls;
            this.click_product_tmpl_handler = function(){
                var product_tmpl = self.pos.db.product_tmpls[this.dataset.productId];
                var product_widget = this;
                if(!product_tmpl) {
                    alert('This product is not available!');
                    $(product_widget).remove();
                }
                else {
                    if(product_tmpl.product_variant_ids.length > 1){
                        self.gui.show_popup('product_variants', {
                            'title' : _t('Please select product variants'),
                            'product_tmpl' : product_tmpl,
                            'image_url' : self.get_product_tmpl_image_url(product_tmpl),
                            'product_widget' : self,
                        });
                    }
                    else{
                        var product = self.pos.db.get_product_by_id(product_tmpl.product_variant_ids[0]);
                        if(product) options.click_product_action(product);
                        else {
                            alert('This product is not available!');
                            $(product_widget).remove();
                        }
                    }
                }
            };
            this.product_tmpl_cache = new screens.DomCache();
        },
        render_product_tmpl: function(product){
            var image_url = this.get_product_tmpl_image_url(product);
            var product_html = QWeb.render('Product',{
                  widget:  this,
                  product: product,
                  image_url: image_url,
            });
            var product_node = document.createElement('div');
            product_node.innerHTML = product_html;
            product_node = product_node.childNodes[1];
            this.product_tmpl_cache.cache_node(product.id,product_node);
            return product_node;
        },
        get_product_tmpl_image_url: function(product){
            return window.location.origin + '/web/image?model=product.template&field=image_medium&id='+product.id;
        },
        renderElement: function() {
            var el_str  = QWeb.render(this.template, {widget: this});
            var el_node = document.createElement('div');
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];
            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;

            var list_container = el_node.querySelector('.product-list');
            for(var i = 0, len = this.product_tmpl_ids.length; i < len; i++){
                var product_tmpl = this.product_tmpls[this.product_tmpl_ids[i]];
                if(product_tmpl.product_variant_ids.length > 1){
                    var product_node = this.render_product_tmpl(this.product_tmpls[this.product_tmpl_ids[i]]);
                    product_node.addEventListener('click',this.click_product_tmpl_handler);
                    list_container.appendChild(product_node);
                }else{
                    var product = this.pos.db.get_product_by_id(product_tmpl.product_variant_ids[0]);
                    if(product){
                        var product_node = this.render_product(product);
                        product_node.addEventListener('click', this.click_product_handler);
                        list_container.appendChild(product_node);
                    }
                }

            }
        },
    });

});