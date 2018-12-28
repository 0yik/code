/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_multiple_receipts.pos_multiple_receipts', function (require) {
"use strict";
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var devices = require('point_of_sale.devices');
	var chrome = require('point_of_sale.chrome');
	var PosBaseWidget = require('point_of_sale.BaseWidget');
	var SuperOrder = models.Order.prototype;
	var QWeb = core.qweb;
	var _t = core._t;

	models.load_models({
		model: 'pos.order.printer',
		fields: [],
		domain: function(self){ 
			var printers_id = [];
			if(self.config.iface_print_via_proxy && self.config.allow_multiple_receipt_printer)
				printers_id = self.config.wk_printer_ids;
		
			return [['id','in', printers_id]]; 
		},
		loaded: function(self,printers){
			self.active_printers = [];
			self.db.printer_by_id = {};
			for(var i = 0; i < printers.length; i++){
				var printer = new devices.ProxyDevice(self);
				printer.config = printers[i];
				self.db.printer_by_id[printers[i].id] = printer;
				self.active_printers.push(printer); 
			}
		},
	});

	models.Order = models.Order.extend({
		initialize: function(attributes,options){
			var self = this;
			this.order_printed = false;
			SuperOrder.initialize.call(this,attributes,options);
		},
	});
	
	var PrinterWidget = PosBaseWidget.extend({
		template: 'PrinterWidget',
		start: function(){
			var self = this;
			var printers = self.pos.active_printers
			printers.forEach(function(printer){
				self.connect_to_printers(printer);
				self.set_status(printer.get('status').status,printer.config.id);
			});
			
			this.$el.on("mouseover click",function(event){
				$('.printer_dropdown').show();
				$('.printer_select').css({'background-color':'#6ec89b'})
			});
			this.$el.on("mouseout",function()
			{
				$('.printer_dropdown').hide();
				$('.printer_select').css({'background-color':''})
			});

			self.$('.printer_name').on("mouseover",function()
			{
				$(this).css('background-color','rgb(62, 36, 36)');
			});

			self.$('.printer_name').on('click',function(event){
				var printer_id = parseInt(this.id);
				var printer = self.pos.db.printer_by_id[printer_id];
				if (printer){
					self.connect_to_printers(printer);
					self.set_status(printer.get('status').status,printer_id)
				}
			});
		},
		status: ['connected','connecting','disconnected'],
		
		set_status: function(status,printer_id){
			printer_id = printer_id.toString();
			for(var i = 0; i < this.status.length; i++){
				this.$('#'+printer_id+' '+'.printer_'+this.status[i]).addClass('oe_hidden');
				$('.printer_select center b p').addClass('oe_hidden');
			}
			
			if($('.printer_disconnected').not('.oe_hidden').length && status == "connected"){
				$('.printer_select center b p').addClass('oe_hidden');
				this.$('.all_disconnected').removeClass('oe_hidden');
			}
			else if(status == "connecting"){
				$('.printer_select center b p').addClass('oe_hidden');
				this.$('.all_connecting').removeClass('oe_hidden');
			}
			else{
				this.$('.all_'+status).removeClass('oe_hidden');
			}
			this.$('#'+printer_id+' '+'.printer_'+status).removeClass('oe_hidden');

		},
		
		connect_to_printers: function(printer){
			var self = this;
			var  done = new $.Deferred();
			this.chrome.loading_message(_t('Connecting to the other PosBox'),0);
			this.chrome.loading_skip(function(){
					printer.stop_searching();
				});
			printer.autoconnect({
					force_ip: printer.config.wk_proxy_ip || undefined,
					progress: function(prog){ 
						self.chrome.loading_progress(prog);
					},
				}).always(function(){
					done.resolve();
					self.set_status(printer.get('status').status,printer.config.id)
				});
			return done;
		},
	});

	chrome.Chrome.prototype.widgets.unshift({
		'name':   'multi_printer',
		'widget': PrinterWidget,
		'append':  '.pos-rightheader',
		'condition': function(){ return this.pos.config.wk_printer_ids.length && this.pos.config.allow_multiple_receipt_printer && this.pos.config.iface_print_via_proxy;},
	});

	
	screens.ReceiptScreenWidget.include({
		print_xml: function() {
			var self = this;
			var no_of_print = self.pos.config.no_of_print_for_proxy_ip
			if (no_of_print > 0){
				self._super();
			}
			if(! self.pos.get_order().order_printed){
				var delay_value = 5000;
				var env = {
					widget:  self,
					receipt: self.pos.get_order().export_for_printing(),
					paymentlines: self.pos.get_order().get_paymentlines()
				};
				var receipt = QWeb.render('DuplicateXmlReceipt',env);
				if (no_of_print > 1){
					for(var len = 1; len < no_of_print; len++){
						setTimeout(function(){
							self.pos.proxy.print_receipt(receipt);
						},delay_value*len)	
					}
					self.pos.get_order()._printed = true;
				}
				var printers = self.pos.active_printers;
				printers.forEach(function(printer){
					for(var len = 1; len <= printer.config.no_of_print; len++){
						setTimeout(function(){
							printer.print_receipt(receipt);
						},delay_value*len)
					}
				});	
			}
			self.pos.get_order().order_printed = true;
		},
	});
});