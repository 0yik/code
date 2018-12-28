odoo.define('pos_promotion_popup.pos_promotion_popup', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;

    var Orderline = models.Orderline.prototype;
    var Order = models.Order.prototype;
    var gui = require('point_of_sale.gui');

    var promotion_select_button = screens.ActionButtonWidget.extend({
        template: 'promotion_select_button',
        default_title: 'Promotion',
        button_click: function () {
            var self = this;
            self.gui.show_popup('choose_promotion_widget');
        },
    });

    screens.define_action_button({
        'name': 'promotion_select_button',
        'widget': promotion_select_button,
    });

    screens.ProductScreenWidget.include({
		show: function(){
			var self = this;
			this._super();
            if(!this.pos.is_promotion_selected){
                this.pos.gui.show_popup('choose_promotion_widget');
            }
		},
	});

    models.load_models([{
			model: 'pos.promotion.days',
			fields: ['id', 'name'],
			loaded: function(self, days) {
			    self.db.pos_promotion_days_by_id = {};
                for (var index in days){
				    self.db.pos_promotion_days_by_id[days[index].id.toString()] = days[index];
                }
			},
	}]);

    for (var index in gui.Gui.prototype.popup_classes) {
        if(gui.Gui.prototype.popup_classes[index].name=='confirm'){
            var ConfirmWidget = gui.Gui.prototype.popup_classes[index].widget;
            var ChoosePromotionWidget = ConfirmWidget.extend({
                template: 'ChoosePromotionWidget',
                title:  'Promotion Today !',
                init: function (parent, options) {
                    this._super(parent, options);
                },
                click_cancel: function() {
                    this._super();
                    this.pos.is_promotion_selected = true;
                },
                show: function(options) {
                    var self = this;
                    this.pos.promotions = this.pos.list_promotion ? this.pos.list_promotion : this.pos.promotions;
                    self.promotions = [];
                    this.pos.promotions.forEach(function (item) {
                        if(item.start_date){
                            if(item.start_date)var start_time = new Date(item.start_date).getTime();
                            if(item.end_date)var end_time = new Date(item.end_date).getTime();
                            var current_time = new Date().getTime();
                            if(!item.start_date || start_time < current_time){
                                if (!item.end_date || current_time < end_time){
                                    if(item.week_days_ids.length == 0 || self.pos.promo_check_in_days(item.week_days_ids)){
                                        if(!item.hours || self.pos.promo_check_in_hours(item.hours)){
                                            self.promotions.push(item);
                                        }
                                    }
                                }
                            }
                        }
                    });
                    this._super(options);
                    this.$('.promotion-line').click(function () {
                        var line_id = $(this).attr('data-id');
                        self.pos.promotion_selected = self.pos.promotion_by_id[line_id];
                        self.pos.is_promotion_selected = true;
                        self.gui.screen_instances.products.action_buttons.promotion_select_button.renderElement();
                        self.pos.list_promotion = self.pos.promotions;
                        self.pos.promotions = [self.pos.promotion_selected];
                        self.gui.close_popup();
                        var order = self.pos.get_order();
                        if (order.orderlines.length) {
                            if (self.pos.promotion_selected.type == '1_discount_total_order') {
                                order.compute_discount_total_order(self.pos.promotion_selected);
                            }
                            if (self.pos.promotion_selected.type == '2_discount_category') {
                                order.compute_discount_category(self.pos.promotion_selected);
                            }
                            if (self.pos.promotion_selected.type == '3_discount_by_quantity_of_product') {
                                order.compute_discount_by_quantity_of_products(self.pos.promotion_selected);
                            }
                            if (self.pos.promotion_selected.type == '4_pack_discount') {
                                order.compute_pack_discount(self.pos.promotion_selected);
                            }
                            if (self.pos.promotion_selected.type == '5_pack_free_gift') {
                                order.compute_pack_free_gift(self.pos.promotion_selected);
                            }
                            if (self.pos.promotion_selected.type == '6_price_filter_quantity') {
                                order.compute_price_filter_quantity(self.pos.promotion_selected);
                            }
                        }
                    })
                },
            });
            gui.define_popup({name:'choose_promotion_widget', widget: ChoosePromotionWidget});
            break;
        }
        // promotion_popup
    }

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        promo_check_in_days: function (array_ids) {
            var self = this;
            var d = new Date();
            var weekday = new Array(7);
            weekday[0] = "Sunday";
            weekday[1] = "Monday";
            weekday[2] = "Tuesday";
            weekday[3] = "Wednesday";
            weekday[4] = "Thursday";
            weekday[5] = "Friday";
            weekday[6] = "Saturday";
            var result = false;
            var day = weekday[d.getDay()];
            array_ids.forEach(function (item) {
                if(self.db.pos_promotion_days_by_id[item] && self.db.pos_promotion_days_by_id[item].name == day){
                    result = true;
                }
            });
            return result
        },
        promo_check_in_hours: function (string) {
            var period = string.split(',');
            var result = false;
            period.forEach(function (item) {
                var hours = item.trim().split('-');
                var current_hour = new Date().getHours();
                if(parseInt(hours[0]) < current_hour && current_hour < parseInt(hours[1])){
                    result = true;
                }
            });
            return result;
        },
    });

});
