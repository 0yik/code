odoo.define('pos_sarang_oci_layout.tax-service', function (require) {
"use strict";
    var session = require('web.session');
    var screens = require('point_of_sale.screens');
    var pos_model = require('point_of_sale.models');
    var OrderWidget = screens.OrderWidget;
    var total;
    var Model = require('web.DataModel');
    var core = require('web.core');
    var _t = core._t;

    var config = pos_model.load_fields("pos.config", "charge");

    pos_model.load_models([{
        model: 'res.branch',
        fields: ['id','name','service_charge_id','tax_id'],
        loaded: function(self, branch) {
            self.db.branch = branch;
        },
	}]);
    pos_model.load_models([{
        model: 'service.charge',
        fields: ['id','name','service_charge_computation','amount'],
        loaded: function(self, charge) {
            self.db.service_charge = charge;
        },
	}]);
    pos_model.load_models([{
        model: 'account.tax',
        fields: ['id','name','amount_type','amount'],
        loaded: function(self, charge) {
            self.db.tax_charge = charge;
        },
	}]);


    var ServiceCharges = screens.ActionButtonWidget.extend({
        template: 'ServiceCharges',

        service_charge_claculate_from_branch_logic: function() {

        },
       
        button_click: function() {
            if ($('button.js_service_charge_button').hasClass('service-charge-apply')){
                var self = this;
                this.gui.show_popup('number', {
                    'title':  _t('Enter PIN Number'),
                    'cheap': true,
                    'value': '',
                    'confirm': function(value) {
                        var pin = $('.popup-input').text();
                        if(!pin.trim()){
                            alert('Please Enter PIN First!')
                            return false
                        }
                        else{
                            var order = this.pos.get_order();
                            var user = this.pos.get_cashier();
                            var username = $('.username')
                            var model = new Model('res.users');
                            var user_id = this.pos.user.id;
                            if(this.pos.check_pin_number(pin)){
                                self.service_charge_change();
                            }else{
                                alert("You have entered a wrong PIN")
                            }
                            // model.call("compare_pin_number", [pin]).then(function (result) {
                            //         if (result){
                            //             self.service_charge_change();
                            //         }
                            //         else{
                            //             alert("You have entered a wrong PIN")
                            //         }
                            // });
                        }
                    },
                });
            }else{
                this.service_charge_change();
            }
    	},
        service_charge_change: function () {
            $('button.js_service_charge_button').toggleClass('service-charge-apply');
            var self = this;
            var order = this.pos.get_order();
            var sub_total = order.get_total_without_tax();
            //var sub_total_without_discount = order.get_total_without_tax() + order.get_total_discount();
            var svm = order.get_service_charge_be();
            if(svm){
                var service_ce = svm.service_charge_computation === 'percentage_of_price' ? ((sub_total* svm.amount)/100).toFixed(2) : svm.amount;
            }else{
                var service_ce = 0;
            }
            if(!$('button.js_service_charge_button').hasClass('service-charge-apply')){
                service_ce = 0;
                order.is_used_charge = false;
            }else{
                order.is_used_charge = true;
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

            var total_bef = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            var rounding = (total_bef %500);
            var total = total_bef - rounding;

            $('.summary .total .subentry .value').text(this.format_currency(parseFloat(pb1)));
            $('.summary .total .subservice .value').text(this.format_currency(parseFloat(service_ce)));
            $('.summary .total .sub-total .value').text(this.format_currency(sub_total));
            // $('.summary .total > .total-bef-rounding > .value').text(this.format_currency(total_bef));
            $('.summary .total .rounding .value').text(this.format_currency(parseFloat(rounding)));
            $('.summary .total .total-total .value').text(this.format_currency(parseFloat(total)));
        	order.save_to_db();
        }
    });

    

    screens.define_action_button({
        'name': 'ServiceCharges',
        'widget': ServiceCharges
    });


    var _super_Order = pos_model.Order.prototype;
    pos_model.Order = pos_model.Order.extend({

        init_from_JSON: function(json) {
            _super_Order.init_from_JSON.call(this, json);
            this.tax_charge_value = json.tax_charge_value;
        },
        export_as_JSON: function() {
            var ret=_super_Order.export_as_JSON.call(this);
            ret.tax_charge_value = this.tax_charge_value;
            return ret;
        },
        add_product:function(product, options){
            
            var r = _super_Order.add_product.call(this, product, options);
            this.pos.gui.screen_instances["products"].action_buttons.ServiceCharges.service_charge_claculate_from_branch_logic()
                        
        }
    });        




    var TaxNonCharge = screens.ActionButtonWidget.extend({
        template: 'TaxNonCharge',
        button_click: function() {
            if ($('button.tax-non-discount-button').hasClass('tax-apply')){
                var self = this;
                this.gui.show_popup('number', {
                    'title':  _t('Enter PIN Number'),
                    'cheap': true,
                    'value': '',
                    'confirm': function(value) {
                        var pin = $('.popup-input').text();
                        if(!pin.trim()){
                            alert('Please Enter PIN First!')
                            return false
                        }
                        else{
                            var order = this.pos.get_order();
                            var user = this.pos.get_cashier();
                            var username = $('.username')
                            var model = new Model('res.users');
                            var user_id = this.pos.user.id;
                            if(this.pos.check_pin_number(pin)){
                                self.tax_charge_change();
                            }else{
                                alert("You have entered a wrong PIN")
                            }
                            // model.call("compare_pin_number", [pin]).then(function (result) {
                            //         if (result){
                            //             self.tax_charge_change();
                            //         }
                            //         else{
                            //             alert("You have entered a wrong PIN")
                            //         }
                            // });
                        }
                    },
                });
            }else{
                this.tax_charge_change();
            }


    	},
        tax_charge_change:function () {
            $('button.tax-non-discount-button').toggleClass('tax-apply');
            var self = this;
            var order = this.pos.get_order();
            var sub_total = order.get_total_without_tax();
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

            var total_bef = parseFloat(sub_total) + parseFloat(service_ce) + parseFloat(pb1);
            var rounding = (total_bef %500);
            var total = total_bef - rounding;

            // $('.summary .total .subentry .value').text(this.format_currency(parseFloat(pb1)));
            // $('.summary .total .subservice > .value').text(this.format_currency(parseFloat(service_ce)));
            // $('.summary .total > .sub-total > .value').text(this.format_currency(sub_total));
            // // $('.summary .total > .total-bef-rounding > .value').text(this.format_currency(total_bef));
            // $('.summary .total > .rounding > .value').text(this.format_currency(parseFloat(rounding)));
            // $('.summary .total > .total-total > .value').text(this.format_currency(parseFloat(total)));
            $('.summary .total .subentry .value').text(this.format_currency(parseFloat(pb1)));
            $('.summary .total .subservice .value').text(this.format_currency(parseFloat(service_ce)));
            $('.summary .total .sub-total .value').text(this.format_currency(sub_total));
            // $('.summary .total > .total-bef-rounding > .value').text(this.format_currency(total_bef));
            $('.summary .total .rounding .value').text(this.format_currency(parseFloat(rounding)));
            $('.summary .total .total-total .value').text(this.format_currency(parseFloat(total)));
        	order.save_to_db();
        }

    });


    screens.define_action_button({
        'name': 'TaxNonCharge',
        'widget': TaxNonCharge
    });


    return {
        ServiceCharge : ServiceCharge,
        TaxNonCharge: TaxNonCharge,
    }
});
