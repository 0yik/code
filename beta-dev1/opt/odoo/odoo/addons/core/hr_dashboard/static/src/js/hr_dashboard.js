odoo.define('hr_dashboard.dashboard', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var bday_emp = []
var aday_emp = []
var absent_emps = []
var late_emps = []
var on_leave = []
var event = []
var months = ''

var HrDashboardView = KanbanView.extend({
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard',
    view_type: "hr_dashboard_view",
    searchview_hidden: true,

    events: {
    	'click .btn_action_open': 'on_dashboard_action_open_clicked',
        'click .btn_action_join': 'on_dashboard_action_join_clicked',
        'click .btn_action_notice': 'on_dashboard_action_notice_clicked',
        'click .btn_action_probation': 'on_dashboard_action_probation_clicked',
        'click .btn_action_leave': 'on_dashboard_action_leave_clicked',
        'click .btn_action_absent': 'on_dashboard_action_absent_clicked',
        'click .btn_action_late_emp': 'on_dashboard_action_late_clicked',
        'click .btn_action_event': 'on_dashboard_action_event_clicked',
        'click .a_bday_action': 'on_dashboard_href_bday_clicked',
        'click .a_aday_action': 'on_dashboard_href_aday_clicked',
        'click .a_iqama_action': 'on_dashboard_href_iqama_clicked',
    },

    fetch_data: function() {
        // Overwrite this function with useful data
        return $.when();
    },

    render: function() {
        var super_render = this._super;
        var self = this;
        return this.fetch_data().then(function(result){
            self.show_demo = result && result.nb_opportunities === 0;
            var employee = new Model('hr.dashboard')
            			.call('get_hr_dashboard_details').then(function(details){
            				bday_emp.push(details['bday_details'])
            				aday_emp.push(details['aday_details'])
            				absent_emps.push(details['absent_emp'])
            				late_emps.push(details['late_emp_id'])
            				on_leave.push(details['on_leave_emp'])
            				months = details['month_date']
            				var s_dashboard = QWeb.render('hr_dashboard.HrDashboard', {
            	                widget: self,
            	                show_demo: self.show_demo,
            	                values: result,
            	                bday_details: details['bday'],
            	                aday_details: details['aday'],
            	                emp_recruit:details['emp_recruit'],
            	                emp_recruit_perc:details['emp_recruit_perc'],
            	                join_emp : details['join_emp_len'],
            	                join_emp_perc :details['join_emp_perc'],
            	                notice_emp : details['notice_emp_len'],
            	                notice_emp_perc : details['notice_emp_perc'],
            	                probation_emp : details['probation_emp_len'],
            	                probation_emp_perc : details['probation_emp_perc'],
            	                emp_on_leave : details['emp_on_leave'],
            	                emp_on_leave_perc: details['emp_on_leave_perc'],
            	                bday_emp: details['bday_details'],
            	                aday_emp: details['aday_details'],
            	                absent_emp: details['absent_emp_len'],
            	                absent_emp_perc: details['absent_emp_perc'],
            	                late_emp: details['late_emp_len'],
            	                late_emp_perc: details['late_emp_perc'],
            	                avg_age: details['comp_avg_age'],
            	                total_emp: details['total_emp'],
            	                event_name: details['event_name'],
            	                event_len: details['event_len'],
            					month_date : details['month_date'],
            	            });
            	            super_render.call(self);
            	            $(s_dashboard).prependTo(self.$el);
            			});
        });
    },

    on_dashboard_action_open_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        this.do_action(action_name);
    },

    on_dashboard_action_join_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        this.do_action(action_name);
    },
    
    on_dashboard_action_notice_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        this.do_action(action_name);
    },
    
    on_dashboard_action_probation_clicked: function(ev){
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        this.do_action(action_name);
    },
    
    on_dashboard_action_leave_clicked: function(ev){
        ev.preventDefault();
        this.do_action({
            name: "Employee on Leave Today",
            res_model: 'hr.holidays',
            views: [[false, 'list'], [false, 'form']],
            type: 'ir.actions.act_window',
            view_type: "list",
            view_mode: "list",
            domain: [['id','in',on_leave[0]]],
        });
    },
    
    on_dashboard_action_absent_clicked: function(ev){
        ev.preventDefault();

        this.do_action({
            name: "Today's Absent Employee",
            res_model: 'hr.employee',
            views: [[false, 'list'],
                    [false, 'form'],
                    [false, 'kanban'],
            		],
            type: 'ir.actions.act_window',
            view_type: "list",
            view_mode: "list",
            domain: [['id','in',absent_emps[0]]],
        });
    },
    
    on_dashboard_action_late_clicked: function(ev){
        ev.preventDefault();

        this.do_action({
            name: "Today's Late Employee",
            res_model: 'hr.attendance',
            views: [[false, 'list'],
                    [false, 'form'],
            		],
            type: 'ir.actions.act_window',
            view_type: "list",
            view_mode: "list",
            domain: [['id','in',late_emps[0]]],
        });
    },
    
    on_dashboard_action_event_clicked: function(ev){
    	console.log("event ::::::::")
//        ev.preventDefault();
//        this.do_action({
//            name: "Upcoming Event",
//            res_model: 'event.event',
//            views: [[false, 'list'], [false, 'form']],
//            type: 'ir.actions.act_window',
//            view_type: "list",
//            view_mode: "list",
//            domain: [['id','in',event[0]]],
//        });
    },
    
    on_dashboard_href_bday_clicked: function(ev){
        ev.preventDefault();
        
        this.do_action({
            name: 'Employee Birthdays'+ '('+ months + ')',
            res_model: 'hr.employee',
            views: [[false, 'list'], [false, 'form'],[false, 'kanban']],
            type: 'ir.actions.act_window',
            view_type: "list",
            view_mode: "list",
//            search_view_id: "hr_holidays_autoallocation.view_employee_filter_search_view_level",
            domain: [['id','in',bday_emp[0]]],
        });
    },
    
    on_dashboard_href_aday_clicked: function(ev){
        ev.preventDefault();
        
        this.do_action({
            name: 'Work Anniversaries' +  '('+ months + ')',
            res_model: 'hr.employee',
            views: [[false, 'list'],
                    [false, 'form'],
                    [false, 'kanban'],
            		],
            type: 'ir.actions.act_window',
            view_type: "list",
            view_mode: "list",
            domain: [['id','in',aday_emp[0]]]
            	
        });
    },
});

core.view_registry.add('hr_dashboard_view', HrDashboardView);

return HrDashboardView;

});
