odoo.define('pos_sarangoci_modifier_receipt.pos_sarangoci_modifier_receipt', function (require) {
"use strict";

    var models = require('point_of_sale.models');
	var _super_posmodel = models.PosModel.prototype;
	var screens = require('point_of_sale.screens');
	var POSSCREEN = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');

	// screens.ReceiptScreenWidget.include({
	// 	renderElement: function() {
	// 		var self = this;
	// 		this._super();
	// 		this.$('.previewbutton').click(function(){
	// 			self.gui.show_screen('receipt');
	// 		});
	// 	},
	// });

	POSSCREEN.PaymentScreenWidget.include({
		renderElement: function() {
            var self = this;
            this._super();
            this.$('.previewbutton').click(function(){
                self.pos.get_order().previewb = true;
                self.gui.show_screen('receipt');
            });
        },

        validate_order: function(force_validation) {

            this.pos.get_order().previewb = false;
            this._super(force_validation);
        },
	});

	POSSCREEN.ReceiptScreenWidget.include({
	    click_back: function(){
            this.gui.show_screen('payment');
        },
		renderElement: function() {
            var self = this;
            this._super();

            this.$('.back').click(function(){
                self.click_back();
            });

        },
        show: function(){
	    	this._super();
            var self = this;
            if(this.pos.get_order() && this.pos.get_order().previewb){
                $('.receipt-screen').find('.next').addClass('oe_hidden')
                $('.receipt-screen').find('.back').removeClass('oe_hidden')
            }
            else{
                $('.receipt-screen').find('.next').removeClass('oe_hidden')
                $('.receipt-screen').find('.back').addClass('oe_hidden')
            }
        },
		handle_auto_print: function () {
			if(!this.pos.get_order().previewb){
				this._super();
			}
        }
	});
	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
        initialize: function(session, attributes) {
            _super_order.initialize.apply(this,arguments);
            this.previewb    = false;
        },

    });

});
