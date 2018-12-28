odoo.define('pos_last_sold_price.pos', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var Model = require('web.DataModel');

var QWeb = core.qweb;

	var LastSoldPrice = screens.ActionButtonWidget.extend({
        template: 'LastSoldPrice',

        button_click: function(){
        	var self = this;
        	var order = this.pos.get_order();
	        var lines = order.get_orderlines();
	        var orderLines = [];
	        var length = order.orderlines.length;
	        for (var i=0;i<length;i++){
	        		orderLines.push(lines[i].export_as_JSON());
	        }
	        if(orderLines.length === 0){
	        	alert("No product selected !");
	        }
	        if(self.pos.get_order().get_selected_orderline()){
	        	var prod = self.pos.get_order().get_selected_orderline().get_product();
				var client = self.pos.get_order().get_client();
				if (client == null){
					alert("No customer selected !");
				}
	        	var prod_info = [];
                var last_date = 0;
                var last_price = 0;
                new Model('sale.order').call('get_last_sold_price',[prod.id,client.id]).then(function(result){
                if(result){
                	last_date = result[0];
                    last_price = result[1];
                    var prod_info_data = "";
					prod_info_data += "<tr>"+
					"	<td style='color:gray;font-weight: bolder !important;padding:5px;text-align: left;padding-left: 15px;' >" + prod.display_name+"</td>"+
					"	<td style='color:gray;font-weight: bolder !important;padding:5px;text-align: center;padding-left: 15px;' >" +last_price+"</td>"+
					"	<td style='color:gray;font-weight: bolder !important;padding:5px;text-align: right;padding-right: 15px;'>"+last_date+"</td>"+
					"</tr>";
                    self.gui.show_popup('last_sold_price_popup',{prod_info_data:prod_info_data});
                }
		    	}).fail(function (error, event){
			        if(error.code === -32098) {
			        	alert("Server closed...");
			        	event.preventDefault();
		           }
		    	});
	        }
        },
    });
    screens.define_action_button({
        'name': 'last_sold_price',
        'widget': LastSoldPrice,
    });

    var LastSoldPricePopupWidget = PopupWidget.extend({
	    template: 'LastSoldPricePopupWidget',
	    show: function(options){
	        options = options || {};
	        this.prod_info_data = options.prod_info_data || '';
	        this.total_qty = options.total_qty || '';
	        this._super(options);
	        this.renderElement();
	    },
	    click_confirm: function(){
	        this.gui.close_popup();
	    },
	    
	});
	gui.define_popup({name:'last_sold_price_popup', widget: LastSoldPricePopupWidget});

});
