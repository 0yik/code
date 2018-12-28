odoo.define('project_issue_start_stop.web_timer', function (require) {
"use strict";

var core = require('web.core');
var common = require('web.form_common');
var Model = require('web.Model');
var time = require('web.time');

var _t = core._t;

var IssueTimeCounter = common.AbstractField.extend(common.ReinitializeFieldMixin, {
    start: function() {
        this._super();
        var self = this;
        this.field_manager.on("view_content_has_changed", this, function () {
            self.render_value();
        });
    },

    start_time_counter: function(){
        var self = this;
        this.timer = null;
        this.duration += 1000;
        this.timer = setTimeout(function() {
            self.start_time_counter();
        }, 1000);
        this.$el.html($('<span>' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
    },

    render_value: function() {
        this._super.apply(this, arguments);
        var self = this;
        if(this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        this.duration;
        if (this.get("effective_readonly")) {
            if (this.field_manager.datarecord.date_end) {
                self.$el.removeClass('o_form_field_empty');
                self.duration = 0;
                self.duration = self.get_date_difference(this.field_manager.datarecord.date_start, this.field_manager.datarecord.date_end);
                self.$el.html($('<span>' + Math.floor(this.duration.asHours()) + moment.utc(this.duration.asMilliseconds()).format(":mm:ss") + '</span>'));
            } else if (this.field_manager.datarecord.date_start){
                self.$el.removeClass('o_form_field_empty');
                var current_date = new Date();
                self.duration = 0;
                self.duration = self.get_date_difference(time.auto_str_to_date(this.field_manager.datarecord.date_start), current_date);
                self.start_time_counter();
            } else {
                self.$el.html($('<span>' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
            }
        }
    },

    get_date_difference: function(date_start, date_end) {
        var difference = moment(date_end).diff(moment(date_start));
        return moment.duration(difference);
    },
});

core.form_widget_registry.add('web_issue_time_counter', IssueTimeCounter);
});
