odoo.define('hr_orgchart_det_branch.FollowupHrDashboardView', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');
    var HrDashboardView = require('hr_dashboard.dashboard_inherit');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var FollowupHrDashboardView = HrDashboardView.extend({
        events: _.defaults({
            'click .btn_action_org_charts_deptment': 'on_dashboard_action_charts_deptment_click',
            'click .btn_action_org_charts_branch': 'on_dashboard_action_org_charts_branch',
        }, HrDashboardView.prototype.events),
        on_dashboard_action_charts_deptment_click: function(ev){
            ev.preventDefault();
            var $action = $(ev.currentTarget);
            var self = this;
            self.deptElement = document.getElementById("deptemp");
            if (self.deptElement ) {
                var display = self.deptElement.style.display;
                if (display === 'block') {
                    self.deptElement.style.display = 'none';
                    return;
                } else if (display === 'none') {
                    self.deptElement.style.display = 'block';
                    return;
                }
                self.getDatasDept();
            }
            this.$el.css('color', '');
        },
        on_dashboard_action_org_charts_branch: function(ev){
            ev.preventDefault();
            var $action = $(ev.currentTarget);
            var self = this;
            self.deptElement = document.getElementById("branchemp");
            console.log('Branch Click....',self.deptElement);
            if (self.deptElement ) {
                var display = self.deptElement.style.display;
                if (display === 'block') {
                    self.deptElement.style.display = 'none';
                    return;
                } else if (display === 'none') {
                    self.deptElement.style.display = 'block';
                    return;
                }
                self.getDatasBranch();
            }
            this.$el.css('color', '');
        },
        getDatasDept: function() {
            return $.ajax({
                url: '/hr_employee/get_full_org_chart_deptment',
                method: 'GET',
                data: {},
                success: $.proxy(this.renderOrgChartDeptment, this),
            });
        },
        getDatasBranch: function() {
            return $.ajax({
                url: '/hr_employee/get_full_org_chart_branch',
                method: 'GET',
                data: {},
                success: $.proxy(this.renderOrgChartBranch, this),
            });
        },
        renderOrgChartDeptment: function(data) {
            var chartData = JSON.parse(data);
            var dataSource = chartData.dataSource;

            if (dataSource.length <= 1) {
                this.do_notify('No hierarchy position.');
                return;
            }

            var renderOrgChartDeptment = new getOrgChartDept(this.deptElement, {
                primaryFields: ["name","manager_id","total_employees","work_email", "work_phone", "mobile_phone"],
                photoFields: ["image"],
                parentIdField:"child_id",
                color: "black",
                scale: 0.5,
                linkType: "M",
                enableEdit: false,
                enableZoom: true,
                enableMove: true,
                theme: "OdooTheme",
                enableGridView: true,
                enableSearch: true,
                enableDetailsView: false,
                enableZoomOnNodeDoubleClick: false,
                expandToLevel: chartData.expandToLevel,
                dataSource: dataSource,
                customize: chartData.customize,
                clickNodeEvent: this.redirectNode,
                renderNodeEvent: this.renderNodHandler,
            });

            this.deptElement.style.display = 'block';
            setInterval(function(){
                $('a[href="http://getorgchartdept.com"]').hide();
            }, 0);
        },
        renderOrgChartBranch: function(data){
            var chartData = JSON.parse(data);
            var dataSource = chartData.dataSource;

            if (dataSource.length <= 1) {
                this.do_notify('No hierarchy position.');
                return;
            }

            var renderOrgChartDeptment = new getOrgChartDept(this.deptElement, {
                primaryFields: ["name","manager_id","total_employees","work_email", "work_phone", "mobile_phone"],
                photoFields: false,
                parentIdField:"child_id",
                color: "black",
                scale: 0.5,
                linkType: "M",
                enableEdit: false,
                enableZoom: true,
                enableMove: true,
                theme: "OdooTheme",
                enableGridView: true,
                enableSearch: true,
                enableDetailsView: false,
                enableZoomOnNodeDoubleClick: false,
                expandToLevel: chartData.expandToLevel,
                dataSource: dataSource,
                customize: chartData.customize,
                clickNodeEvent: this.redirectNode,
                renderNodeEvent: this.renderNodHandler,
            });

            this.deptElement.style.display = 'block';
            setInterval(function(){
                $('a[href="http://getorgchartdept.com"]').hide();
            }, 0);
        },
    });
    core.view_registry.add('hr_dashboard_view', FollowupHrDashboardView);

    return FollowupHrDashboardView;
});


