odoo.define('pos_promotion_multiselection', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require("point_of_sale.popups");
    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;


     models.load_models([
    {
            model: 'pos.promotion.days',
            fields: [],
            context: {'pos': true},
            loaded: function (self, promotions_week_days) {
                self.promotions_week_days = promotions_week_days;
                self.promotions_week_days_by_id = {};
                self.promotions_week_days_ids = []
                var i = 0;
                while (i < promotions_week_days.length) {
                    self.promotions_week_days_by_id[promotions_week_days[i].id] = promotions_week_days[i];
                    self.promotions_week_days_ids.push(promotions_week_days[i].id);
                    i++;
                }
            }
        }
    ]);
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            var self = this;
            var res = _super_order.initialize.apply(this, arguments);
            self.pos.date_object = new Date();
            var weekday = new Array(7);
            weekday[0] = "Sunday";
            weekday[1] = "Monday";
            weekday[2] = "Tuesday";
            weekday[3] = "Wednesday";
            weekday[4] = "Thursday";
            weekday[5] = "Friday";
            weekday[6] = "Saturday";
            self.pos.weekday = weekday[self.pos.date_object.getDay()];
            return res;
        },

    	auto_build_promotion: function () {
            if (!this.pos.building_promotion || this.pos.building_promotion == false) {
                if (this.pos.config.allow_promotion == true && this.pos.config.promotion_ids.length) {
                    this.pos.building_promotion = true;
                    var promotions = this.pos.promotions

                    if (promotions) {
                        for (var i = 0; i < promotions.length; i++) {
                            var type = promotions[i].type
                            var order = this;
                            var current_day = false;
                            var current_time = (promotions[i].hours ? false : true);
                            console.log(" 6222 622222 62  ", current_time);
                            var hours = promotions[i].hours;
                            var index = 0;
                            var hours_list = [];
                            if(hours && hours.indexOf(',', index) != -1){
                                while (hours.indexOf(',', index) != -1){
                                    hours_list.push(hours.substring(index, hours.indexOf(',', index)))
                                    index = hours.indexOf(',', index) +1;
                                }
                                hours_list.push(hours.substring(hours.lastIndexOf(',')+1 ))
                            }
                            if(hours && hours.indexOf(',') == -1){
                                hours_list.push(hours);
                            }
                            for (var j = promotions[i].week_days_ids.length -1 ; j >= 0; j--) {
                                console.log("this.pos.promotions_week_days[i] idddddddd ", promotions[i].week_days_ids[j], this.pos.weekday);
                                if(this.pos.promotions_week_days_by_id[promotions[i].week_days_ids[j]].name == this.pos.weekday){
                                    current_day = true;
                                }
                            }
                            var start_time = false;
                            for (var j = hours_list.length - 1; j >= 0; j--){
                                var end = hours_list[j].substring(hours_list[j].indexOf('-') +1, hours_list[j].length).trim();
                                var start = hours_list[j].substring(0, hours_list[j].indexOf('-')).trim();
                                if(parseInt(start) <= parseInt(this.pos.date_object.getHours()) &&  parseInt(end) > parseInt(this.pos.date_object.getHours()) ){
                                    current_time = true;
                                }
                               
                            }
                            
                            console.log("\n\n\t\t\t>>>>>>>>current_day && current_time ", current_day ,current_time);
                            if (order.orderlines.length && current_day && current_time) {
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
                            }
                        }
                    }
                    this.pos.building_promotion = false;
                }
            }
        },

    });
});