odoo.define('pos_membership_cards.pos_membership_cards', function (require) {
"use strict";
	var pos_model = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var popup_widget = require('point_of_sale.popups');
	var gui = require('point_of_sale.gui');
	var Model = require('web.DataModel');
	var core = require('web.core');
	var SuperOrder = pos_model.Order;
	var _t = core._t;

	pos_model.Order = pos_model.Order.extend({
		initialize: function(attributes,options){
			self = this;
			self.membership_card_used = false;
			self.membership_applied_discount;
			var card_dict;
			SuperOrder.prototype.initialize.call(this,attributes,options);
		},
	});
	var MembershipAlertPopup = popup_widget.extend({
		template: 'MembershipAlertPopup',
		
	});
	gui.define_popup({ name: 'alert_message', widget: MembershipAlertPopup });

	var MembershipCardPopup = popup_widget.extend({
		template:'MembershipCardPopup',
		events: {
			'click .button.cancel':  'click_cancel',
			'click .button.confirm': 'click_confirm',
			'click .selection-item': 'click_item',
			'click .input-button':   'click_numpad',
			'click .mode-button':    'click_numpad',
			'click #check_card':     'click_check_card',
			'click #wk_apply':     	 'click_apply_discount',
			'keyup #card_code': 	 'key_press_input',
		},

		membership_card_action:function(code){
			
			this.$("#card_code").val(code.code)
			this.click_check_card();

		},

		show: function(){
			var self = this;
			self._super();
			this.pos.barcode_reader.set_action_callback({
	            'product': _.bind(self.membership_card_action, self),
	        });

		},

		click_cancel: function(){
			var self = this;
			this.gui.close_popup();
			if (this.options.cancel) {
				this.options.cancel.call(this);
			}
			window.document.body.addEventListener('keypress',self.chrome.screens.payment.keyboard_handler);
			window.document.body.addEventListener('keydown',self.chrome.screens.payment.keyboard_keydown_handler);
		},
		click_apply_discount: function(){
			var self = this;
			var client = self.pos.db.get_partner_by_id(self.pos.get_order().card_dict.customer_id);
			self.pos.chrome.screens.products.order_widget.numpad_state.reset();
			var discount_sum = 0;
			self.pos.get_order().orderlines.models.forEach(function(line){
				discount_sum = discount_sum + line.get_discount();
			});
			if(self.pos.get_order().paymentlines.length >0){
				self.pos.get_order().paymentlines.models = [];
				self.gui.chrome.screens.payment.render_paymentlines();
			}
			
			if((discount_sum == 0) || (self.pos.config.override_existing_discount && self.pos.config.override_selection == 'all_existing_discounts'))
			{
				self.pos.get_order().set_client(client);
				self.pos.get_order().orderlines.models.forEach(function(line){
					self.pos.get_order().select_orderline(line);
					line.set_discount(self.pos.get_order().card_dict.discount);
				});
				self.pos.chrome.screens.payment.render_paymentlines();
				self.pos.get_order().membership_card_used = true;
				self.pos.get_order().membership_applied_discount = self.pos.get_order().card_dict.discount;
				$("#membership_discount").html("<b>"+self.pos.get_order().card_dict.discount+"% Membership Discount Applied</b>");
				$("#membership_discount").show();
			}
			else
			{
				if(self.pos.config.override_existing_discount && self.pos.config.override_selection == 'only_less_discounts')
				{
					var applied = false;
					self.pos.get_order().orderlines.models.forEach(function(line){
						if(line.get_discount() < self.pos.get_order().card_dict.discount)
						{
							self.pos.get_order().select_orderline(line);
							line.set_discount(self.pos.get_order().card_dict.discount);
							applied = true;
						}
					});
					if(applied)
					{
						self.pos.get_order().set_client(client);
						self.pos.chrome.screens.payment.render_paymentlines();
						self.pos.get_order().membership_card_used = true;
						self.pos.get_order().membership_applied_discount = self.pos.get_order().card_dict.discount;
						$("#membership_discount").html("<b>"+self.pos.get_order().card_dict.discount+"% Membership Discount Applied</b>");
						$("#membership_discount").show();
					}
				}
				else if(self.pos.config.ignore_membership_discount && self.pos.config.ignore_selection == 'only_where_discounts_exists')
				{
					var applied = false;
					self.pos.get_order().orderlines.models.forEach(function(line){
						if(line.get_discount() == 0)
						{
							self.pos.get_order().select_orderline(line);
							line.set_discount(self.pos.get_order().card_dict.discount);
							applied = true;
						}
					});
					if(applied)
					{
						self.pos.get_order().set_client(client);
						self.pos.chrome.screens.payment.render_paymentlines();
						self.pos.get_order().membership_card_used = true;
						self.pos.get_order().membership_applied_discount = self.pos.get_order().card_dict.discount;
						$("#membership_discount").html("<b>"+self.pos.get_order().card_dict.discount+"% Membership Discount Applied</b>");
						$("#membership_discount").show();
					}
				}	
			}
			self.click_cancel();
		},
		key_press_input: function(e){
			var self = this;
			var key = e.which;
			if(key == 13)  // the enter key code
			{
				self.click_check_card()
			}
			else if(key == 46)
			{
				self.$('#card_code').val("");
			}
		},
		click_check_card: function(){
			var self = this;
			var card_code;
			if($("#card_code").val()!='')
			{
				card_code = self.$("#card_code").val();
				new Model('pos.membership.card').call('get_card_details',[{"card_code":card_code}])
				.fail(function(unused, event){
					event.preventDefault();
					self.gui.play_sound('error');
					self.gui.show_popup('error',{
						title: _t('Failed To Fetch Card Details.'),
						body:  _t('Please make sure you are connected to the network.'),
					});
				})
				.done(function(card_details)
				{
					self.pos.get_order().card_dict = card_details;
					if(card_details.status)
					{
						var msg;
						msg = "<table width=100%><tr><td>Customer Name:</td><td>"+self.pos.get_order().card_dict.customer_name+"</td></tr><tr><td>Membership :</td><td>"+self.pos.get_order().card_dict.card_category+" ("+self.pos.get_order().card_dict.discount+"% OFF)</td></tr></table>"
						self.$('#card_error').hide();
						self.$('#delete_paymentlines_alert').hide();

						self.$('#card_valid').html(msg);
						self.$('#card_valid').show();
						self.$('#wk_apply').show();
						var discount = self.pos.get_order().card_dict.discount
						if(self.pos.get_order().paymentlines.length >0){
							self.$('#delete_paymentlines_alert').text("After applying membership-discount, all payment lines will be removed")
							self.$('#delete_paymentlines_alert').show();
						}
					}
					else
					{
						self.$('#card_valid').hide();
						self.$('#wk_apply').hide();
						self.$('#delete_paymentlines_alert').hide();
						self.$('#card_error').text(self.pos.get_order().card_dict.message)
						self.$('#card_error').css("height","46%");
						self.$('#card_error').show();
						self.gui.play_sound('error');
					}
				});
			}
		}
	});
	gui.define_popup({name:'membership_card_popup', widget: MembershipCardPopup});

	screens.PaymentScreenWidget.include({
		show: function(){
			var self = this;
			this.pos.get_order().clean_empty_paymentlines();
			this.reset_input();
			this.render_paymentlines();
			this.order_changes();
			window.document.body.addEventListener('keypress',this.keyboard_handler);
			window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
			this._super();
			self.$('#membership_card').click(function(){
				if(self.pos.get_order().get_total_with_tax() > 0)
				{
					self.gui.show_popup('membership_card_popup',{});
					window.document.body.removeEventListener('keypress',self.keyboard_handler);
					window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
					$('#card_code').focus();
				}
				else
				{
					self.gui.show_popup('alert_message',{
						'title': _t('Zero Payment Amount'),
						'body':  _t('To apply membership-card payment amount must be greater than zero'),
					});
				}
			});
			if(!self.pos.get_order().membership_card_used)
				$("#membership_discount").hide();
		},
	});
});