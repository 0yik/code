odoo.define('pos_screen_for_variants.pos_variants_popup', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var PopupWidget = require('point_of_sale.popups');
    var QWeb = core.qweb;

    var ProductVariantsPopupWidget = PopupWidget.extend({
        template: 'ProductVariantsPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
        }),
        init: function(parent, options){
            this._super(parent, options);
            this.product_variants = [];
        },
        show: function (options) {
            this._super(options);
            var self = this;
            var lines = []
            var list_container = this.el.querySelector('.pick-attribute');
            if(!options.product_tmpl) this.gui.close_popup();
            this.image_url = options.image_url;
            _.map(options.product_tmpl.attribute_line_ids, function (attribute_line) {
                var line = self.pos.db.attribute_lines[attribute_line];
                line.values = [];
                _.map(line.value_ids, function (value) {
                    line.values.push(self.pos.db.attribute_values[value]);
                })
                lines.push(self.pos.db.attribute_lines[attribute_line]);
            })

            var lines_node = QWeb.render('AttributeLinePopupWidget', {
                'lines' : lines,
                'image_url' : options.image_url,
            });
            //product_node.addEventListener('click',this.click_product_tmpl_handler);
            list_container.innerHTML = lines_node;
        }
    });
    gui.define_popup({name:'product_variants', widget: ProductVariantsPopupWidget});

    return ProductVariantsPopupWidget;
});