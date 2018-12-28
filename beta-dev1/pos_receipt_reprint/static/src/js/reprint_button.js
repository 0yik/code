odoo.define('pos_receipt_reprint.pos_reprint_button', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var QWeb = core.qweb;
var Model = require('web.DataModel');

var ButtonRePrintPopupWidget = PopupWidget.extend({
    template: 'ButtonRePrintPopupWidget',

    events: {
        'click .button.cancel':  'click_cancel',
        'click .button.print_kitchen': 'click_print_kitchen',
	'click .button.print_bar': 'click_print_bar',
    },

    click_print_kitchen : function(){
	var order = this.pos.get_order();
        var orderline = order.orderlines;
	this.gui.screen_instances['reprint-receipt'].print(true, false)
    },

    click_print_bar : function(){

	var order = this.pos.get_order();
        var orderline = order.orderlines;
	this.gui.screen_instances['reprint-receipt'].print(false, true)
    },
});
gui.define_popup({name:'reprint_button', widget: ButtonRePrintPopupWidget});

var RePrintReceiptScreenWidget = screens.ScreenWidget.extend({
    template: 'RePrintReceiptScreenWidget',

    show: function(){
        this._super();
        var self = this;
        this.render_receipt();
    },
    print_xml: function(kitchen, bar) {
	var order = this.pos.get_order();
	var lines = order.orderlines.models;
	var orderlines = [];
	var note = [];
	var table =''
	if(this.pos.table){
	    table = this.pos.table.name
	}
	for(var i = 0; i < lines.length; i++){
//    	lines[i].state === 'Confirmed' && 
        if(lines[i].is_printed != 1){
            orderlines.push(lines[i])
            note.push(lines[i].note)
            lines[i].is_printed = 1
        }
    }
	var receipt_data = this.pos.get_order().export_for_printing()
    for(var i = 0; i < receipt_data.orderlines.length; i++){
    	receipt_data.orderlines[i].note = note[i]
    }
    console,log('Receipt   '+receipt_data)
	var env = {
        widget:  this,
        pos: this.pos,
        order: this.pos.get_order(),
        receipt: receipt_data,
        table: table,
    };
    var receipt = QWeb.render('XmlReceiptreprint',env);
	//var flag = false;
	if (kitchen == true){
	    var printers = this.pos.printers
	    var pos = this.pos
	    new Model("restaurant.printer").call("search_read", [[["name", "ilike", 'kitchen']]]).then(function(result){
		for(var i = 0; i < printers.length; i++){
		    if(result[0].id != printers[i].config.id){
			pos.printers.pop(printers[i])
			pos.printers.pop(printers[i])
			pos.proxy.print_receipt(receipt);
        		pos.get_order()._printed = true;

		    }
	    	}
		
	    })
	}
	if (bar == true){
	    var printers = this.pos.printers
	    var pos = this.pos
	    new Model("restaurant.printer").call("search_read", [[["name", "ilike", 'bar']]]).then(function(result){
		for(var i = 0; i < printers.length; i++){
	            console.log('CCCCCCCCCCCCCCCCCCCC', printers[i], printers[i].config.name)
		    if(result[0].id != printers[i].config.id){
			pos.printers.pop(printers[i])
			pos.printers.pop(printers[i])
			pos.proxy.print_receipt(receipt);
        		pos.get_order()._printed = true;
		    }
	    	}
		
	    })
	}
    },
    print_web: function() {
        window.print();
        this.pos.get_order()._printed = true;
    },
    print: function(kitchen, bar) {
        var self = this;
        if (!this.pos.config.iface_print_via_proxy) { // browser (html) printing

            // The problem is that in chrome the print() is asynchronous and doesn't
            // execute until all rpc are finished. So it conflicts with the rpc used
            // to send the orders to the backend, and the user is able to go to the next 
            // screen before the printing dialog is opened. The problem is that what's 
            // printed is whatever is in the page when the dialog is opened and not when it's called,
            // and so you end up printing the product list instead of the receipt... 
            //
            // Fixing this would need a re-architecturing
            // of the code to postpone sending of orders after printing.
            //
            // But since the print dialog also blocks the other asynchronous calls, the
            // button enabling in the setTimeout() is blocked until the printing dialog is 
            // closed. But the timeout has to be big enough or else it doesn't work
            // 1 seconds is the same as the default timeout for sending orders and so the dialog
            // should have appeared before the timeout... so yeah that's not ultra reliable. 

            this.lock_screen(true);
		
            setTimeout(function(){
            }, 1000);

            this.print_web();
        } else {    // proxy (xml) printing
	    console.log('ELLLLLLLLLLLLLLLLL')
            this.print_xml(kitchen, bar);
        }
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.button.print').click(function(){
		console.log('capl-print0')
        	self.print();
        });
    },
    render_receipt: function() {
        var order = this.pos.get_order();
	var lines = order.orderlines.models;
	var orderlines = [];
        for(var i = 0; i < lines.length; i++){
            if(lines[i].state === 'Confirmed' && lines[i].is_printed != 1){
                orderlines.push(lines[i])
		lines[i].is_printed = 1
            }
        }
        this.$('.pos-print-receipt-container').html(QWeb.render('PosReceipt',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: orderlines,
            }));
    },
    
});
gui.define_screen({name:'reprint-receipt', widget: RePrintReceiptScreenWidget});

var ReprintKitchenbarButton = screens.ActionButtonWidget.extend({
    template: 'ReprintKitchenbarButton',
    button_click: function() {
	var order = this.pos.get_order();
	var lines = order.orderlines.models
 	var flag = 0
	for(var i = 0; i < lines.length; i++){
            if(lines[i].state != 'Confirmed' && lines[i].state != 'Done'){
		flag = 1;
               
            }
        }
	if(flag === 1){
		alert('You have no confirmed order!')
	}
	else if (order.orderlines.length > 0){
		this.gui.show_popup('reprint_button', {
		    'body': 'Printer Option?'
		});
	}
	else{
		alert('There are not orderlines selected.')	
	}
	this.reprint=this.value;
    }
    });

    screens.define_action_button({
        'name': 'ReprintKitchenbarButton',
        'widget': ReprintKitchenbarButton,
    });
return {
ReprintKitchenbarButton : ReprintKitchenbarButton,
RePrintReceiptScreenWidget : RePrintReceiptScreenWidget,
ButtonRePrintPopupWidget : ButtonRePrintPopupWidget,
};

});
