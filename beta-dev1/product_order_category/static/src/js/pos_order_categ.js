odoo.define('product_order_category.product_order_category', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
    var SubmitOrderButton = require('pos_restaurant.multiprint');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var _t  = require('web.core')._t;
    var screens = require('point_of_sale.screens');
    var pos_model = require('point_of_sale.models');

    models.load_fields('product.product',['product_order_category_ids']);

    pos_model.load_models([{
        model:  'pos.order.category',
        fields: ['name','notes', 'card_color'],
        loaded: function(self, order_category){
            var order_category_by_id = {}
            var order_category_by_name = {}
            for (var i = order_category.length - 1; i >= 0; i--) {
                order_category_by_id[order_category[i].id] = order_category[i]
                order_category_by_name[order_category[i].name] = order_category[i]
            }
            self.db.order_category = order_category_by_id
            self.order_category_by_name = order_category_by_name
        },
    }]);


    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var QWeb = core.qweb;
    var _super_order = models.Order.prototype;
    var floors = require('pos_restaurant.floors');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        build_line_resume: function(){
            var resume = {};
            var self = this
            
            this.orderlines.each(function(line){
                var product_id = self.pos.db.get_product_by_id(line.product.id)
                if(!product_id){
                    self.orderlines.remove(line);
                    self.select_orderline(self.get_last_orderline());
                }
            });
            
            this.orderlines.each(function(line){
                if (line.mp_skip) {
                    return;
                }
                var line_hash = line.get_line_diff_hash();

                // DIFFERENCES FROM ORIGINAL:
                // * getting qty, note, product_id is moved to a separate function
                // * add line_id value
                var line_resume = self.get_line_resume(line);

                if (typeof resume[line_hash] === 'undefined') {
                    resume[line_hash] = line_resume;
                } else {
                    resume[line_hash].qty += line_resume.qty;
                }
            });
            return resume;
        },
    });
    return models;
});