odoo.define('delivery_charges.pos_order', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');


    models.load_models([{
        model: 'res.branch',
        fields: ['id','name','delivery_charge_id'],
        loaded: function(self, branch) {
            self.db.branch = branch;
        },
	}]);
    models.load_models({
        model: 'order.charge',
        fields: ['id', 'name','type','amount'],
        domain: null,
        loaded: function(self,charges){
            console.log(charges);
            self.db.charges = charges;
        },
    });
    models.Order = models.Order.extend({
        // get_total_with_tax: function() {
        //     let charge = this.pos.category == 'delivery' ? this.get_order_charge() : 0;
        //     return this.get_total_without_tax() + this.get_total_tax() + charge;
        // },
        get_order_charge: function () {
            var order_charge = 0;
            var untaxed_amount = this.get_total_without_tax();
            var branch_id = this.pos.config.branch_id && this.pos.config.branch_id[0];
            if(branch_id){
                for(let i=0; i<this.pos.db.branch.length; i++){
                    if(this.pos.db.branch[i].id == branch_id){
                        let order_charge_id = this.pos.db.branch[i].delivery_charge_id[0];
                        for(let j=0; j<this.pos.db.charges.length; j++){
                            if(this.pos.db.charges[j].id == order_charge_id){
                                if(this.pos.db.charges[j].type == 'percentage'){
                                    order_charge = untaxed_amount*this.pos.db.charges[j].amount/100;
                                }else if (this.pos.db.charges[j].type == 'fixed'){
                                    order_charge = this.pos.db.charges[j].amount;
                                }
                            }
                        }
                    }
                }
            }
            return order_charge;
        }
    });
    screens.OrderWidget.include({
       update_summary: function(){
           this._super();
           var order = this.pos.get_order();
            if (!order.get_orderlines().length) {
                return;
            }
            if(this.pos.category == 'delivery'){
                var order_charge = order ? order.get_order_charge() : 0;
                var total     = order ? order.get_total_with_tax() + order_charge: 0;
                var taxes = order ? order.get_total_tax() : 0;

                this.el.querySelector('.summary .total .deliverycharge > .value').textContent = this.format_currency(order_charge);
                this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
                this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
            }else{
                this.el.querySelector('.summary .total .deliverycharge').style.display = 'none';
            }

       },
    });
});
