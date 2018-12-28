odoo.define('pos_hide_cancel_button.pos_hide_cancel_button', function (require) {
"use strict";
	var pos_orders = require('pos_orders.pos_orders');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var QWeb = core.qweb;
	var _t = core._t;
	var chrome = require('point_of_sale.chrome');
	
	chrome.SynchNotificationWidget.include({
	    start: function(){
	    	this._super();
	        var current_order = this.pos.get_order();
	        if(current_order != null && current_order.is_return_order){
	        	$('#cancel_refund_order').show();
	        }
	        else
	        {
	        	$('#cancel_refund_order').hide();
	        }
	    },
	});	
});