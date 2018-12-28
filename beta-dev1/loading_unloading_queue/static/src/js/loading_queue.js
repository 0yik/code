odoo.define('loading_unloading_queue.loading_queue_time', function (require) {
"use strict";

var core = require('web.core');
var common = require('web.form_common');
var Model = require('web.Model');
var time = require('web.time');
var utils = require('web.utils');
var FieldBinaryFile = core.form_widget_registry.get('binary');

var _t = core._t;

//  loading_queue_time_counter

var QueueTimeCounter = common.AbstractField.extend(common.ReinitializeFieldMixin, {
    start: function() {
        this._super();
        var self = this;
        this.field_manager.on("view_content_has_changed", this, function () {
            self.render_value();
        });
    },
    start_time_counter: function(){
        var self = this;
        clearTimeout(this.timer);
        if (this.field_manager.datarecord.check) {
            this.duration += 1000;
            this.timer = setTimeout(function() {
                clearTimeout(this.timer);
                self.start_time_counter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
        this.$el.html($('<span>' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
    },
    render_value: function() {
        this._super.apply(this, arguments);
        var self = this;
        this.duration;

        var loading_queue_domain = [['id', '=', this.field_manager.datarecord.id]];
        new Model('loading.queue').call('search_read', [loading_queue_domain, []]).then(function(result) {
            if (self.get("effective_readonly")) {
                self.$el.removeClass('o_form_field_empty');
                var current_date = new Date();
                self.duration = 0;
                _.each(result, function(data) {
                    self.duration += data.end_time ? self.get_date_difference(data.start_time, data.end_time) : self.get_date_difference(time.auto_str_to_date(data.start_time), current_date);
                });
                self.start_time_counter();
            }
        });
    },
    get_date_difference: function(date_start, date_end) {
        var difference = moment(date_end).diff(moment(date_start));
        return moment.duration(difference);
    },
});

core.form_widget_registry.add('loading_queue_time_counter', QueueTimeCounter);
});
