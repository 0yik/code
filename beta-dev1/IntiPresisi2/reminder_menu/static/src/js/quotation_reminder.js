odoo.define('reminder_menu.reminder_menu', function (require) {
    "use strict";

var bus = require('bus.bus').bus;
var core = require('web.core');
var Model = require('web.Model');
var CalendarView = require('web_calendar.CalendarView');
var data = require('web.data');
var Dialog = require('web.Dialog');
var SystrayMenu = require('web.SystrayMenu');
var WebClient = require('web.WebClient');
var weblient = require('web.web_client');
var widgets = require('web_calendar.widgets');
var Widget = require('web.Widget');
var UserMenu = require('web.UserMenu');
var Menu = require('web.Menu');
var session = require('web.session');
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;
    var user_obj = ''

    var QuotationReminder = Widget.extend({
        sequence: 100, // force it to be the left-most item in the systray to prevent flickering as it is not displayed in all apps
        template: "QuotationReminder",
        events: {
            "click": "on_menu_clicked",
        },
        init: function(parent) {
            this._super(parent);
        },
        start: function() {
            var self = this;
            var waiting_order = [];
            var res_user = new Model('res.users');
            res_user.call('search_read', [[['id', '=', self.session.uid]]]).then(function(res) {
                _.each(res, function(user) {
                    user_obj = user
                });
            });
            var sale_order = (new Model('sale.order')).query().all().then(function(order) {
                _.each(order, function(sale) {
                    if (sale.state == 'sent'){
                        if (sale.user_id[0] == self.session.uid){
                            waiting_order.push(sale);
                        }else{
                            if (user_obj.admin_b == true || user_obj.president_director_b == true || user_obj.sales_supervisor_b == true){
                                waiting_order.push(sale);
                            }
                        }
                    }
                    
                });
            })

            sale_order.done(function() {
                var total_count = waiting_order.length;
                $('.o_reminder_counter').text(total_count);
                var widget = $('.o_reminder_dropdown_channels', this.$el).html(QWeb.render('reminder_order',{
                    order: waiting_order,
                }));
            });
        },
        on_menu_clicked: function(menu_id) {
            var self = this;
            $('.recorddata').click(function(){
                if ( $(this).attr('id') ){
                    self.open_ui($(this).attr('id'));
                }
            });
        },
        open_ui: function(sale_id){
            var self = this;

            if (sale_id) {
                var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'sale.order',
                    views: [[false, "form"]],
                    res_id: parseInt(sale_id),
                };
                self.do_action(action,{clear_breadcrumbs: true});
            }
        },
    });

    SystrayMenu.Items.push(QuotationReminder);

    return {
        QuotationReminder: QuotationReminder,
    };

});