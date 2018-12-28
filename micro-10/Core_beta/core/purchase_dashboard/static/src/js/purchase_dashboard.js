odoo.define('purchase_dashboard.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

// var bday_emp = []
// var aday_emp = []
// var absent_emps = []
// var late_emps = []
    var purchase_month = [];
    var purchase_purchase_request_today = [];
    var rfq = [];
    var incoming_shipment = [];
    var pending_shipment = [];
    var invoices = [];
    var purchase_request_to_approve = [];
    var low_stock_products = [];
    var purchase_tender = [];
    var purchase_total = [];

    var months = '';
    var current_year = '';
    var today = ''
    var number_of_vendors;
    var top_ten_vendor;
    var top_ten_amount;
    var PurchaseDashboard = KanbanView.extend({
        display_name: _lt('Dashboard'),
        icon: 'fa-dashboard',
        view_type: "purchase_dashboard_view",
        searchview_hidden: true,

        events: {
            'click .btn_action_purchase_request_today': 'on_dashboard_action_purchase_purchase_request_today_clicked',
            'click .btn_action_rfq_open': 'on_dashboard_action_rfq_open_clicked',
            'click .btn_action_purchase_month_open': 'on_dashboard_action_purchase_month_open_clicked',
            'click .btn_action_purchase_open': 'on_dashboard_action_action_purchase_open_clicked',

            'click .btn_action_open_incoming_shipment': 'on_dashboard_action_open_incoming_shipment',
            'click .btn_action_open_pending_shipment': 'on_dashboard_action_open_pending_shipment',
            'click .btn_action_open_pr_to_approve': 'on_dashboard_action_open_pr_to_approve_clicked',
            'click .btn_action_open_invoices': 'on_dashboard_action_open_invoices_clicked',

            'click .btn_action_open_stock_low_product': 'on_dashboard_action_open_stock_low_product_clicked',
            'click .btn_action_open_tender': 'on_dashboard_action_open_tender_clicked',
            // 'click .btn_action_late_emp': 'on_dashboard_action_late_clicked',
            // 'click .btn_action_event': 'on_dashboard_action_event_clicked',
            // 'click .a_bday_action': 'on_dashboard_href_bday_clicked',
            // 'click .a_aday_action': 'on_dashboard_href_aday_clicked',
            // 'click .a_iqama_action': 'on_dashboard_href_iqama_clicked',
        },

        fetch_data: function () {
            // Overwrite this function with useful data
            return $.when();
        },

        render: function () {
            var super_render = this._super;
            var self = this;
            return this.fetch_data().then(function (result) {
                self.show_demo = result && result.nb_opportunities === 0;
                var employee = new Model('purchase.dashboard')
                    .call('get_purchase_dashboard_details').then(function (details) {
                        purchase_purchase_request_today = details['purchase_purchase_request_today']
                        purchase_month = details['purchase_month'];
                        purchase_total = details['purchase_total'];
                        rfq = details['rfq'];
                        incoming_shipment = details['incoming_shipment'];
                        pending_shipment = details['pending_shipment'];
                        invoices = details['invoices'];
                        purchase_request_to_approve = details['purchase_request_to_approve'];
                        low_stock_products = details['low_stock_products'];
                        purchase_tender = details['purchase_tender'];
                        top_ten_vendor = details['top_ten_vendor'];
                        top_ten_amount = details['top_ten_amount'];
                        current_year = details['current_year'];

                        // number_of_vendors = details['number_of_vendors'];

                        months = details['month_date'];
                        today = details['date_of_today'];
                        var s_dashboard = QWeb.render('purchase_dashboard.HrDashboard', {
                            widget: self,
                            // show_demo: self.show_demo,
                            values: result,
                            'number_of_rfq': details['number_of_rfq'],
                            'total_amount_of_rfq': details['total_amount_of_rfq'],
                            'number_of_purchase_month': details['number_of_purchase_month'],
                            'total_amount_of_purchase_month': details['total_amount_of_purchase_month'],
                            'number_of_purchase_total': details['number_of_purchase_total'],
                            'total_amount_of_purchase_total': details['total_amount_of_purchase_total'],
                            'number_of_purchase_request_today': details['number_of_purchase_request_today'],
                            // 'number_of_vendors': details['number_of_vendors'],
                            'number_of_invoices': details['number_of_invoices'],
                            'currency': details['currency'],
                            'number_of_incoming_shipment': details['number_of_incoming_shipment'],
                            'number_of_pending_shipment': details['number_of_pending_shipment'],
                            'number_purchase_request_to_approve': details['number_purchase_request_to_approve'],
                            'number_of_low_stock_products': details['number_of_low_stock_products'],
                            'number_of_purchase_tender': details['number_of_purchase_tender'],
                        });
                        setTimeout(function () {
                            if (document.getElementById("myChart2")) {
                                var ctx2 = document.getElementById("myChart2").getContext('2d');
                                var data2 = {
                                    labels: top_ten_vendor,
                                    datasets: [{
                                        label: "Dataset #1",
                                        backgroundColor: "rgba(26,93,134,1)",
                                        borderWidth: 2,
                                        hoverBackgroundColor: "rgba(25,123,183,0.6)",
                                        data: top_ten_amount,
                                    }]
                                };
                                var myOpts = {
                                    elements: {
                                        rectangle: {
                                            borderSkipped: 'left',
                                        },
                                    },
                                    onClick: this.chartLink,
                                    animation: false,
                                    legend: {
                                        display: false,
                                    },
                                    tooltips: {
                                        enabled: true,
                                    },
                                    maintainAspectRatio: false,
                                    responsive: true,
                                    scales: {
                                        xAxes: [{
                                            ticks: {
                                                beginAtZero: true,
                                                display: true,
                                            },
                                        }],
                                        yAxes: [{
                                            tabIndex: 0,
                                            maxBarThickness: 100,
                                            categoryPercentage: 1.0,
                                            barPercentage: 1.0,
                                            barThickness: 20,
                                            gridLines: {
                                                display: false,
                                                drawBorder: false,
                                            },

                                        }],
                                    }
                                };
                                var myChart2 = new Chart(ctx2, {
                                    type: 'horizontalBar',
                                    data: data2,
                                    options: myOpts
                                });
                            }

                        }, 500);
                        super_render.call(self);
                        $(s_dashboard).prependTo(self.$el);
                    });
            });
        },
        on_dashboard_action_open_invoices_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Bills To Pay",
                res_model: 'account.invoice',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', invoices]],
            });
        },
        on_dashboard_action_open_tender_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Purchase Tender",
                res_model: 'purchase.requisition',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', purchase_tender]],
            });
        },

        on_dashboard_action_open_stock_low_product_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Low Stock Products",
                res_model: 'product.product',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', low_stock_products]],
            });
        },

        on_dashboard_action_open_pr_to_approve_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Purchase Request To Approve/In Progress",
                res_model: 'purchase.request',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', purchase_request_to_approve]],
            });
        },

        on_dashboard_action_rfq_open_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "RFQ on " + '(' + months + ')',
                res_model: 'purchase.order',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', rfq]],
            });
        },

        on_dashboard_action_action_purchase_open_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Purchase Orders on " + '(' + current_year + ')',
                res_model: 'purchase.order',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', purchase_total]],
            });
        },

        on_dashboard_action_purchase_month_open_clicked: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: "Purchase on " + '(' + months + ')',
                res_model: 'purchase.order',
                views: [[false, 'list'], [false, 'form']],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', purchase_month]],
            });
        },

        on_dashboard_action_purchase_purchase_request_today_clicked: function (ev) {
            ev.preventDefault();

            this.do_action({
                name: "Total Purchase Request ",
                res_model: 'purchase.request',
                views: [[false, 'list'],
                    [false, 'form'],
                ],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', purchase_purchase_request_today]],
            });
        },

        on_dashboard_action_open_incoming_shipment: function (ev) {
            ev.preventDefault();

            this.do_action({
                name: "Today's Incoming Shipment" + '(' + today + ')',
                res_model: 'stock.picking',
                views: [[false, 'list'],
                    [false, 'form'],
                ],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', incoming_shipment]],
            });
        },

        on_dashboard_action_open_pending_shipment: function (ev) {
            ev.preventDefault();

            this.do_action({
                name: "Pending Shipment",
                res_model: 'stock.picking',
                views: [[false, 'list'],
                    [false, 'form'],
                ],
                type: 'ir.actions.act_window',
                view_type: "list",
                view_mode: "list",
                domain: [['id', 'in', pending_shipment]],
            });
        },

    });

    core.view_registry.add('purchase_dashboard_view', PurchaseDashboard);

    return PurchaseDashboard;

});
