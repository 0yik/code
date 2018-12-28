odoo.define('xxi_pos_layout.misc_button', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.Model');
var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var multiprint = require('pos_restaurant.multiprint');
var Backbone = window.Backbone;
var QWeb = core.qweb;
var _t   = core._t;

chrome.Chrome.include({
    build_chrome: function () {
        this._super();
        var today = new Date();
        var time = today.getHours() + ":" + today.getMinutes();
        this.pos['current_time'] = time
    },
});

var MiscButton = screens.ActionButtonWidget.extend({
    template: 'MiscButton',

    button_click: function(){
        var self = this;
        if ($('#misc').hasClass('remove_misc')){
            $('#misc').removeClass('remove_misc');
            $('.control-buttons').find('.main_button').addClass('remove_main');
            $('.control-buttons').find('.remove_main').removeClass('main_button');
            $('.control-buttons').find('.btn-wd').css('display','block');
        }
        else{
            $('#misc').addClass('remove_misc');
            $('.control-buttons').find('.remove_main').addClass('main_button');
            $('.control-buttons').find('.main_button').removeClass('remove_main');
            $('.control-buttons').find('.btn-wd').css('display','none');
            $('.control-buttons').find('.btn-wd').css('display','none');
        }
    },
});

screens.define_action_button({
    'name': 'misc_button',
    'widget': MiscButton,
});

/*Fixed category buttons*/
screens.ProductCategoriesWidget.include({
    set_category : function(category){
        this._super();
        var db = this.pos.db;
        if(!category){
            this.category = db.get_category_by_id(db.root_category_id);
        }else{
            this.category = category;
        }
        this.breadcrumb = [];
        var ancestors_ids = db.get_category_ancestors_ids(this.category.id);
        for(var i = 1; i < ancestors_ids.length; i++){
            this.breadcrumb.push(db.get_category_by_id(ancestors_ids[i]));
        }
        if(this.category.id !== db.root_category_id){
            this.breadcrumb.push(this.category);
        }
        this.subcategories = db.get_category_by_id(db.get_category_childs_ids(this.category.id));
        if (this.category.id != 0){
            this.subcategories = db.get_category_by_id(db.get_category_childs_ids(db.root_category_id));
        }
    },
})

screens.OrderWidget.include({
    update_summary: function(){
        this._super();
        var order = this.pos.get_order();

            if (!order || !order.get_orderlines().length) {
                return;
            }
            var sub_total = order.get_total_without_tax();
            //var sub_total_ext = order.get_sub_total();
            var sub_total_ext = 0;
            //var svm = order.get_service_charge_be();
            var svm = false;
            if(svm){
                var service_ce = svm.service_charge_computation === 'percentage_of_price' ? ((sub_total* svm.amount)/100).toFixed(2) : svm.amount;
            }else{
                var service_ce = 0;
            }
            if(!$('button.js_service_charge_button').hasClass('service-charge-apply')){
                service_ce = 0;
            }
            order.service_charge = service_ce;

            var taxc = sub_total_ext + parseFloat(service_ce);
            //var tax_use = order.get_tax_charge_be();
            var tax_use = false;
            var pb1 = 0;
            if(tax_use){
                pb1 = (tax_use.amount * taxc)/100;
            }
            if(!$('button.tax-non-discount-button').hasClass('tax-apply')){
                pb1 = 0;
            }
            order.tax_charge_value = pb1;
            var total = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            order.amount = total;

            $('.pos .l-table .total-amount .value').remove();
            $('.pos .l-table .total-amount').append('<span class="value" style="font-size:13px"><b>'+this.format_currency(total)+'</b></span>');
        	order.save_to_db();
    }
});

});