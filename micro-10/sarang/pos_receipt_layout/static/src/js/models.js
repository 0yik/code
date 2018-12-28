odoo.define('pos_receipt_layout.pos_receipt_layout', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var _super_posmodel = models.PosModel.prototype;
	var POSSCREEN = require('point_of_sale.screens');


	for (var i=0; i<_super_posmodel.models.length; i++){
	    if (_super_posmodel.models[i].model == 'res.users'){
	        _super_posmodel.models[i].fields.push('branch_id');
	    }
	};
	models.load_models([{
		model: 'res.branch',
		fields: ['id', 'name', 'telephone_no', 'address', 'company_id','service_charge_id'],
		domain: function(self) {
			return [['id', '=', self.user.branch_id[0]]];
		},
		loaded: function(self, branch) {
			self.db.res_branch = branch;
			self.db.order_by_id = {};
		},
	}]);


	models.load_fields('res.company', 'street');
	models.load_fields('res.company', 'street2');
	models.load_fields('res.company', 'city');

	POSSCREEN.ReceiptScreenWidget.include({
		print: function() {
		    var self = this;
		    this._super.apply(this, arguments);
		},
		render_receipt: function() {
		    this._super.apply(this, arguments);
		},
		print_web: function() {
			$('.pos-sale-ticket').each(function () {
				if($(this).parent().hasClass('pos')){
					$(this).remove();
				}
            });
			$('.receipt-screen.screen:not(".oe_hidden") .pos-sale-ticket').clone().appendTo(".pos");
			$('.pos').css('height','1000px');
			this._super.apply(this, arguments);
			$('.pos').css('height','100%');
		},
	});

	models.Orderline = models.Orderline.extend({

        get_total_discount_line: function () {
            return (this.price * this.quantity) - this.get_display_price();
        },
        get_total_price_without_discount: function () {
            return (this.price * this.quantity);
        },
        get_space_from_middle_to_right: function (rightvalue) {
			//22-1(char =) = 21 for right
			var space = 21 - rightvalue.toString().length;
			var result = "";
			for (var i= 0;i<space;i++){
				result+= " ";
			}
			return result;
        },
	});
	models.Order = models.Order.extend({
		get_space_line_total:function (total) {
        	var space = 43 - total.toString().length;
			var result = "";
			for (var i= 0;i<space;i++){
				result+= " ";
			}
			return result;
        },
	});


});