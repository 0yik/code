odoo.define('pos_sarangoci_modifier_payment', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PaymentScreenWidget = screens.PaymentScreenWidget;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var core = require('web.core');
    var _t = core._t;
    models.load_fields("pos.config", "charge");
    models.Order = models.Order.extend({
        get_total_without_tax: function() {
             if(this.all_free){return 0.0};
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                var amount = orderLine.get_complimentary() ? 0 : orderLine.get_price_without_tax();
                return sum + amount;
            }), 0), this.pos.currency.rounding);
        },
        get_total_with_tax: function() {
        	
            if(this.all_free){return 0.0}
            if(this.get_total_without_tax() == 0){
                return 0.0;
            }

            // var sub_total = this.get_total_without_tax();
            // var service_ce = this.service_charge;
            // var pb1 = this.tax_charge_value;
            // var total_bef = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            // var total   = (total_bef - (total_bef % 500));
            // return total;

            var calc = this.calculation_order_confirmed();
            return calc.total;
        },
        get_total_with_tax_without_round: function() {
            if(this.all_free){return 0.0}
            if(this.get_total_without_tax() == 0){
                return 0.0;
            }
            var sub_total = this.get_total_without_tax();
            var service_ce = this.service_charge;
            var pb1 = this.tax_charge_value;
            var total = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            return total
        },
        get_rounding:function () {
            var sub_total = this.get_total_without_tax();
            var service_ce = this.service_charge;
            var pb1 = this.tax_charge_value;
            var total = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            return total%500;
        },
        get_service_charge_be: function () {
            var list_charge = this.pos.db.service_charge;
            var list_branch = this.pos.db.branch;
            var branch_id = this.pos.config.branch_id[0];

            var charge_id = false;
            var result = false;
            list_branch.forEach(function (item, index, arr) {
                if(item.id === branch_id){
                    charge_id = item.service_charge_id ? item.service_charge_id[0] : false;
                }
            });
            list_charge.forEach(function (item, index, arr) {
                if(item.id === charge_id){
                    result = item;
                }
            });
            return result;
        },
        get_tax_charge_be:function () {
            var list_charge = this.pos.db.tax_charge;
            var list_branch = this.pos.db.branch;
            var branch_id = this.pos.config.branch_id[0];

            var charge_id = false;
            var result = false;
            list_branch.forEach(function (item, index, arr) {
                if(item.id === branch_id){
                    charge_id = item.tax_id ? item.tax_id[0] : false;
                }
            });
            list_charge.forEach(function (item, index, arr) {
                if(item.id === charge_id){
                    result = item;
                }
            });
            return result;
        }
    });
    screens.OrderWidget.include({
        update_summary: function(){
            this._super();

            var order = this.pos.get_order();

            if (!order || !order.get_orderlines().length) {
                return;
            }
            var rounding = 0;
            var sub_total = order.get_total_without_tax();

            if(order.get_selected_orderline() && order.get_selected_orderline().is_complimentary){
                $('.Complimentary-orderline-button').addClass('on-green');
            }else{
                $('.Complimentary-orderline-button').removeClass('on-green');
            }
            //var sub_total_without_discount = order.get_total_without_tax() + order.get_total_discount();

            var svm = order.get_service_charge_be();
            if(svm){
                var service_ce = svm.service_charge_computation === 'percentage_of_price' ? ((sub_total* svm.amount)/100).toFixed(2) : svm.amount;
            }else{
                var service_ce = 0;
            }
            if(!$('button.js_service_charge_button').hasClass('service-charge-apply')){
                service_ce = 0;
            }
            order.service_charge = service_ce;


            var taxc = sub_total + parseFloat(service_ce);
            var tax_use = order.get_tax_charge_be();
            var pb1 = 0;
            if(tax_use){
                pb1 = (tax_use.amount * taxc)/100;
            }
            if(!$('button.tax-non-discount-button').hasClass('tax-apply')){
                pb1 = 0;
            }
            order.tax_charge_value = pb1;



            var total = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            if (total > 500){
                rounding   = (total - (total % 500))
            }
            var total_rounding = (total - rounding).toFixed(2);

            this.el.querySelector('.summary .total .subentry .value').textContent = pb1.toFixed(2);
            // this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(pb1);
            this.el.querySelector('.summary .total .subservice .value').textContent = service_ce;
            // this.el.querySelector('.summary .total .subservice .value').textContent = this.format_currency(parseFloat(service_ce));
            this.el.querySelector('.summary .total .sub-total .value').textContent = this.format_currency(parseFloat(sub_total));
            this.el.querySelector('.summary .total .rounding .value').textContent = total_rounding;
            // this.el.querySelector('.summary .total .rounding .value').textContent = this.format_currency(total_rounding);
            this.el.querySelector('.summary .total .total-total .value').textContent = this.format_currency(total - total_rounding);
            this.el.querySelector('.summary .total .subservice .service-percentage').textContent = svm.service_charge_computation === 'percentage_of_price' ? svm.amount + '%' : svm.amount;
            this.el.querySelector('.summary .total .subentry .tax-percentage').textContent = tax_use ? tax_use.amount + '%' : '0%';
        	order.save_to_db();
        	
        },
        change_selected_order:function () {
            var order = this.pos.get_order();
            if(order){
                if(order.is_used_tax===false){
                    this.gui.screen_instances.products.$('button.tax-non-discount-button').removeClass('tax-apply');
                }else{
                    this.gui.screen_instances.products.$('button.tax-non-discount-button').addClass('tax-apply');
                }
                if(order.is_used_charge===false){
                    this.gui.screen_instances.products.$('button.js_service_charge_button').removeClass('service-charge-apply');
                }else{
                    this.gui.screen_instances.products.$('button.js_service_charge_button').addClass('service-charge-apply');
                }
            }
            this._super();
        }
    });
});
