odoo.define('hilti_modifier_customer_booking_dashboard.hilti_modifier_customer_booking_dashboard', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
var KanbanView = require('web_kanban.KanbanView');
var _lt = core._lt;
var Model = require('web.Model');
var session = require('web.session');
var Partner = new Model('res.partner');


var ProjectBookingDashboardView = KanbanView.extend({
    display_name: _lt('Booking Dashboard'),
    icon: 'fa-dashboard',
    searchview_hidden: true,
    events: {
        'click .o_dashboard_action': 'on_dashboard_action_clicked',
        'click .o_dashboard_kanban_action': 'o_dashboard_kanban_action',
        'click .o_kanban_manage_toggle_button': 'toggle_manage_pane',
    },
    toggle_manage_pane: function(event){
        event.preventDefault();
        $(event.currentTarget).closest('.o_kanban_record').find('.o_kanban_card_content').toggleClass('o_visible o_invisible');
        $(event.currentTarget).closest('.o_kanban_record').find('.o_kanban_card_manage_pane').toggleClass('o_visible o_invisible');
    },
    fetch_data: function() {
        // Overwrite this function with useful data
    	return new Model('project.booking')
        	.call('retrieve_booking_dashboard', []);
    },
    start: function(){
    	var self = this;
    	self.type_of_user = '';
    	Partner.call('search_read', [[['id', '=', session.partner_id]], ["type_of_user"]]).done(function(customer) {
    		self.type_of_user = customer[0].type_of_user
    	})
    	return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        
        var booking_action_name_admin = 'hilti_modifier_company.action_admin_booking_view';
        var booking_action_name_tester = 'hilti_modifier_company.action_my_booking_view_tester';
        var booking_action_name_customer = 'hilti_modifier_company.action_my_booking_view';
        
        var request_action_name_admin = 'hilti_modifier_tester_myrequests.action_my_request_admin_view';
        var request_action_name_tester = 'hilti_modifier_tester_myrequests.action_my_request_view';
        
        var booking_action = ''; 
        var request_action = '';
        if (self.type_of_user == 'hilti_admin'){
        	var booking_action = booking_action_name_admin;
            var request_action = request_action_name_admin;
        }else if (self.type_of_user == 'hilti_tester'){
        	var booking_action = booking_action_name_tester;
            var request_action = request_action_name_tester;
        }else if (self.type_of_user == 'hilti_customer'){
        	var booking_action = booking_action_name_customer; 
        }
        
        
        return this.fetch_data().then(function(result){
            var sales_dashboard = QWeb.render('ProjectBookingDashboard', {
                widget: self,
                booking_action: booking_action,
                request_action: request_action,
                type_of_user: self.type_of_user,
                values: result,
            });
            super_render.call(self);
            $(sales_dashboard).prependTo(self.$el);
        });
    },

    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();

        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        var additional_context = {};

        if (action_extra === 'today') {
            additional_context.search_default_today = 1;
        } else if (action_extra === 'this_week') {
            additional_context.search_default_this_week = 1;
        } 
        
        else if (action_extra === 'pending_booking_today') {
            additional_context.search_default_pending_booking_today = 1;
        } else if (action_extra === 'completed_booking_today') {
            additional_context.search_default_completed_booking_today = 1;
        } else if (action_extra === 'delayed_booking_today') {
            additional_context.search_default_delayed_booking_today = 1;
        }
        
        else if (action_extra === 'pending_booking_this_month') {
            additional_context.search_default_pending_booking_this_month = 1;
        } else if (action_extra === 'completed_booking_this_month') {
            additional_context.search_default_completed_booking_this_month = 1;
        } else if (action_extra === 'delayed_booking_this_month') {
            additional_context.search_default_delayed_booking_this_month = 1;
        }
        
        else if (action_extra === 'pending_booking_last_month') {
            additional_context.search_default_pending_booking_last_month = 1;
        } else if (action_extra === 'completed_booking_this_month') {
            additional_context.search_default_completed_booking_last_month = 1;
        } else if (action_extra === 'delayed_booking_last_month') {
            additional_context.search_default_delayed_booking_last_month = 1;
        }
            
        this.do_action(action_name, {additional_context: additional_context});
    },

    o_dashboard_kanban_action: function(ev){
    	var self = this;
    	
    	var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        var additional_context = {};
    	
    	if (action_extra === 'delayed_start') {
            additional_context.search_default_delayed_start = 1;
    	}else if (action_extra === 'delayed_end') {
            additional_context.search_default_delayed_end = 1;
    	}else if (action_extra === 'sic_bookings') {
            additional_context.search_default_sic_bookings = 1;
    	}else if (action_extra === 'normal_bookings') {
            additional_context.search_default_normal_bookings = 1;
    	}else if (action_extra === 'dedicated_support') {
            additional_context.search_default_dedicated_support = 1;
    	}else if (action_extra === 'vip_bookings') {
            additional_context.search_default_last_minute = 1;
    	}else if (action_extra === 'vip_customers') {
            additional_context.search_default_vip_customers = 1;
    	}else if (action_extra === 'non_vip_customers') {
            additional_context.search_default_non_vip_customers = 1;
    	}else if (action_extra === 'unavailable_request') {
            additional_context.search_default_unavailable_request = 1;
//            additional_context.search_default_groupby_user_id = 1;
    	}else if (action_extra === 'overtime_request') {
            additional_context.search_default_overtime_request = 1;
    	}else if (action_extra === 'pending_bookings') {
    		additional_context.search_default_status = 1;
    		additional_context.search_default_projects = 1;
    	}else if (action_extra === 'active_users') {
    		additional_context.search_default_active_users = 1;
    	}else if (action_extra === 'inactive_users') {
    		additional_context.search_default_Inactive = 1;
    	}
    	
    	
    	
    	
    	this.do_action(action_name, {additional_context: additional_context});
    },


});

core.view_registry.add('project_booking_dashboard', ProjectBookingDashboardView);


});