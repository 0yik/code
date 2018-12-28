odoo.define('hilti_modifier_booking_notification.hilti_modifier_booking_notification', function (require) {
    "use strict";

var core = require('web.core');
var Model = require('web.Model');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var session = require('web.session');
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

    var BookingNotification = Widget.extend({
        sequence: 100,
        template: "BookingNotification",
        events: {
            "click .recorddata": "on_record_click",
            "click #reminder_open": "on_menu_clicked"
        },
        init: function(parent) {
            this._super(parent);
            this.notifications = [];
        },
        start: function() {
            var self = this;
            self.fetch_booking_order();
        },
        fetch_booking_order: function(){
        	var self = this;
        	var bookings = new Model('notification.notification').query([]).filter([["user_ids", "=", session.uid]]).context({'from_notification_window': true}).all().then(function(notifications) {
	            self.notifications = notifications;
	        })
	        bookings.done(function() {
	            $('.o_reminder_counter').text(self.notifications.length);
	            $('.o_reminder_dropdown_channels', this.$el).html(QWeb.render('reminder_order',{
	                orders: self.notifications,
	            }));
	        });
        },
        on_menu_clicked: function(){
        	var self = this;
        	self.fetch_booking_order();
        },
        on_record_click: function(el) {
            var self = this;
            var model = $(el.currentTarget).data('model');
            if (model != 'res.users'){
            	var action = {
                    type: 'ir.actions.act_window',
                    res_model: model,
                    views: [[false, "form"]],
                    res_id: parseInt($(el.currentTarget).data('id')),
                };
                self.do_action(action,{clear_breadcrumbs: true});
            }else{
            	self.do_action('hilti_modifier_loginsignup.action_res_users_inactive', {additional_context: {'search_default_Inactive': 1}});
            }
        },
        
    });

    SystrayMenu.Items.push(BookingNotification);

    return {
    	BookingNotification: BookingNotification,
    };

});