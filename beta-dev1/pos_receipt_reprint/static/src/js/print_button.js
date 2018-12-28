odoo.define('pos_receipt_reprint.pos_print_button', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var QWeb = core.qweb;
var Model = require('web.DataModel');

var ButtonPrintPopupWidget = PopupWidget.extend({
    template: 'ButtonPrintPopupWidget',

    events: {
        'click .button.cancel':  'click_cancel',
        'click .button.print_kitchen': 'click_print_kitchen',
	'click .button.print_bar': 'click_print_bar',
    },

    click_print_kitchen : function(){
	var order = this.pos.get_order();
        var orderline = order.orderlines;
	this.gui.screen_instances['print-receipt'].print(true, false)
    },

    click_print_bar : function(){

	var order = this.pos.get_order();
        var orderline = order.orderlines;
	this.gui.screen_instances['print-receipt'].print(false, true)
    },
});
gui.define_popup({name:'print_button', widget: ButtonPrintPopupWidget});

var PrintReceiptScreenWidget = screens.ScreenWidget.extend({
    template: 'PrintReceiptScreenWidget',

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
//        	lines[i].state === 'Confirmed' && 
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
        var env = {
            widget:  this,
            pos: this.pos,
            order: this.pos.get_order(),
            receipt: receipt_data,
            table: table,
        };
        console.log("receipt_data...........",receipt_data)
        var receipt = QWeb.render('XmlReceipt1',env);
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

            //this.lock_screen(true);
		
            setTimeout(function(){
            }, 1000);

            this.print_web();
        } else {    // proxy (xml) printing
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
		console.log('-IFFFFFFFFFF')
                orderlines.push(lines[i])
		lines[i].is_printed = 1
            }
        }
	console.log('SSSSSSSSSSSSSSSSSSSS', order.get_orderlines(), orderlines)
        this.$('.pos-print-receipt-container').html(QWeb.render('PosReceipt',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: orderlines,
            }));
    },
    
});
gui.define_screen({name:'print-receipt', widget: PrintReceiptScreenWidget});

var PrintKitchenbarButton = screens.ActionButtonWidget.extend({
    template: 'PrintKitchenbarButton',
    
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
		this.gui.show_popup('print_button', {
		    'body': 'Printer Option?'
		});
	}
	
	else{
		alert('There are not orderlines selected.')
	}
    }
    });

    screens.define_action_button({
        'name': 'PrintKitchenbarButton',
        'widget': PrintKitchenbarButton,
    });
return {
	PrintKitchenbarButton: PrintKitchenbarButton,
	PrintReceiptScreenWidget : PrintReceiptScreenWidget,
	ButtonPrintPopupWidget : ButtonPrintPopupWidget
};

});
