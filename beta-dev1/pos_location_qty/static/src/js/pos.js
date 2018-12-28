odoo.define('pos_location_qty.pos', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var Model = require('web.DataModel');

var QWeb = core.qweb;

	var ProductQty = screens.ActionButtonWidget.extend({
        template: 'ProductQty',

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
	        	var prod = self.pos.get_order().get_selected_orderline().get_product()
	        	var prod_info = [];
                var total_qty = 0;
                var total_qty = 0;
                new Model('stock.warehouse').call('disp_prod_stock',[prod.id,self.pos.shop.id]).then(function(result){
                if(result){
                	prod_info = result[0];
                    total_qty = result[1];
                    var prod_info_data = "";
                    var id = 0
                    _.each(prod_info, function (i) {
                    	var detail_line = ""
                    	_.each(i[2], function (j) {
							detail_line += "<tr>"+
                        "	<td style='color:gray;font-weight: initial !important;padding:5px;text-align: left;padding-left: 15px; display: none;' data-id="+id+ " class='detail_location_name detail_location' >"+ "+ " +j[0]+"</td>"+
                        "	<td style='color:gray;font-weight: initial !important;padding:5px;text-align: right;padding-right: 15px; display: none;' data-id="+id+ " class='detail_location_qty detail_location' >" +j[1]+"</td>"+
                        "</tr>";
                        })
                    	prod_info_data += "<tr>"+
                        "	<td style='color:gray;font-weight: bolder !important;padding:5px;text-align: left;padding-left: 15px;' >" +"<a data-id="+id+ " class='drop_down_location'>&#9658;</a> " +i[0]+"</td>"+
                        "	<td style='color:gray;font-weight: bolder !important;padding:5px;text-align: right;padding-right: 15px;'>"+i[1]+"</td>"+
                        "</tr>" + detail_line;
                    	id++;
                    });
                    self.gui.show_popup('product_qty_popup',{prod_info_data:prod_info_data,total_qty: total_qty});
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
        'name': 'product_qty',
        'widget': ProductQty,
    });

    var ProductQtyPopupWidget = PopupWidget.extend({
	    template: 'ProductQtyPopupWidget',
		events: {
        'click .button.cancel':  'click_cancel',
        'click .button.confirm': 'click_confirm',
        'click .selection-item': 'click_item',
        'click .input-button':   'click_numpad',
        'click .mode-button':    'click_numpad',
        'click .drop_down_location': 'drop_down',
        'click .up_location ': 'up'
    	},
		drop_down: function (e) {
        	e.preventDefault();
        	var a_tag = e.target;
        	var tmp_id = a_tag.getAttribute('data-id');
			$('.detail_location[data-id="'+tmp_id+'"]').show();
			$(a_tag).removeClass("drop_down_location").addClass("up_location").html("&#9660;");
        },
		up: function (e) {
			e.preventDefault();
        	var a_tag = e.target;
        	var tmp_id = a_tag.getAttribute('data-id');
			$('.detail_location[data-id="'+tmp_id+'"]').hide();
			$(a_tag).removeClass("up_location").addClass("drop_down_location").html("&#9658;");
        },
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
	gui.define_popup({name:'product_qty_popup', widget: ProductQtyPopupWidget});

});
