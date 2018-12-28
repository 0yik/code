odoo.define('scheduler_notification.Chatter', function (require) {
"use strict";

var scheduler_chatter = require('mail.Chatter');
var thread = require('mail.ChatThread');
var Model = require('web.Model');
var core = require('web.core');
var web_utils = require('web.utils');
var time = require('web.time');
var QWeb = core.qweb;
var _t = core._t;


thread.include({
	render: function (messages, options) {
	    var self = this;
        this._super(messages, options);
        var parent = self.getParent();

        new Model("ir.cron").call("search_read", [[['transaction', '=', parent.model],['res_id', '=', parent.res_id]]]).then(function(results){
        	_.each(results, function (scheduler) {
                scheduler.create_date = moment(time.auto_str_to_date(scheduler.create_date));
                scheduler.end_date = moment(time.auto_str_to_date(scheduler.end_date));
            });

            // sort scheduler by end_date
        	var scheduler_reminder = _.sortBy(results, 'end_date');
            if (scheduler_reminder.length) {
                var nbschedulers = _.countBy(scheduler_reminder, 'status');
                self.$el.find('.o_thread_date_separator:first').prepend(QWeb.render('scheduler_notification.scheduler_items', {
                    schedulers:scheduler_reminder,
                    runningscheduler: nbschedulers.run,
                }));
            }
        });

        /*new Model("ir.cron").call("search_read", [[['transaction', '=', parent.model],['res_id', '=', parent.res_id],['status','=','done'],['active','=',false]]]).then(function(results){
        	_.each(results, function (scheduler) {
                scheduler.create_date = moment(time.auto_str_to_date(scheduler.create_date));
                scheduler.end_date = moment(time.auto_str_to_date(scheduler.end_date));
            });

            // sort scheduler by end_date
        	var scheduler_reminder = _.sortBy(results, 'end_date');
            if (scheduler_reminder.length) {
                var nbdone_schedulers = _.countBy(scheduler_reminder, 'status');
                self.$el.find('.o_thread_date_separator:first').prepend(QWeb.render('scheduler_notification.scheduler_items', {
                    done_schedulers:scheduler_reminder,
                    nbdone_schedulers: nbdone_schedulers.done,
                }));
            }
        });*/

    },
})

scheduler_chatter.include({
    //template: 'mail.Chatter',
    init: function (parent, record, mailFields, options) {
        this._super.apply(this, arguments);
        this.model = this.view.dataset.model;
        this.res_id = undefined;
        this.context = this.options.context || {};
        this.dp = new web_utils.DropPrevious();
        this.activities = [];
    },

    events: _.extend({}, scheduler_chatter.prototype.events, {
        'click .o_chatter_button_schedule_reminder': '_onScheduleReminder',
        'click .o_scheduler_edit': '_onEditScheduler',
        'click .o_scheduler_unlink': '_onUnlinkScheduler',
        'click .o_scheduler_done': '_onDoneLinkScheduler',
    }),

    _onScheduleReminder: function () {
    	var self = this
        var action = {
                type: 'ir.actions.act_window',
                res_model: 'ir.cron',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    search_default_all: 1,
                    default_active: true,
                    default_res_id: this.res_id,
                    default_transaction_model: this.model,
                    default_scheduler_setup: true,
                    default_model: 'scheduler.notification',
                    default_function: 'send_scheduler_notification_email',
                    default_numbercall: -1,
                    record_url:window.location.href,
                },
                res_id:  false,
            };

            return this.do_action(action, {
                on_close: function() {
                    self.trigger('need_refresh');
                	self.render_value()
                },
            });
    },


    _onEditScheduler: function (event, options) {
        var self = this;
        var scheduler_id = $(event.currentTarget).data('scheduler');
        var action = _.defaults(options || {}, {
            type: 'ir.actions.act_window',
            res_model: 'ir.cron',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                scheduler_setup: true,
                default_res_id: this.res_id,
                default_transaction: this.transaction,
                default_transaction_model: this.model,
                default_scheduler_setup: true,
                default_model: 'scheduler.notification',
                default_function: 'send_scheduler_notification_email',
                default_numbercall: -1,
                record_url:window.location.href,
            },
            res_id: scheduler_id,
        });
        return this.do_action(action, {
            on_close: function () {
                // remove the edited scheduler from the array of fetched schedulers to
                // force a reload of that scheduler
                self.schedulers = _.reject(self.schedulers, {id: scheduler_id});
                self.render_value()
            },
        });
    },

    _onUnlinkScheduler: function (event, options) {
        event.preventDefault();
        var self=this;
        var scheduler_id = $(event.currentTarget).data('scheduler');
        options = _.defaults(options || {}, {
            model: 'ir.cron',
            args: [[scheduler_id]],
        });
        return new Model("ir.cron").call("unlink",[[scheduler_id]]).then(function(){
        		self.render_value();
		});
    },

    _onDoneLinkScheduler: function (event, options) {
        event.preventDefault();
        var self=this;
        var scheduler_id = $(event.currentTarget).data('scheduler');
        options = _.defaults(options || {}, {
            model: 'ir.cron',
            args: [[scheduler_id]],
        });
        return new Model("ir.cron").call("write", [[scheduler_id], {'status': 'done', 'active':false}]).then(function(){
        		self.render_value();
		});
    },

});

});
