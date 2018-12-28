odoo.define('mgm_sale_orde_gantt_view.GanttView', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var data_manager = require('web.data_manager');
var formats = require('web.formats');
var Model = require('web.Model');
var time = require('web.time');
var View = require('web.View');
var form_common = require('web.form_common');
var Dialog = require('web.Dialog');

var Model1 = require('web_gantt.GanttView');

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

var GanttView = Model1.extend({
    display_name: _lt('Gantt'),
    events: {
        'click .gantt_task_row .gantt_task_cell': 'create_on_click',
    },
    icon: 'fa-tasks',
    require_fields: true,
    template: 'GanttView',
     init: function () {
        var self = this;
        this._super.apply(this, arguments);
        this.has_been_loaded = $.Deferred();
        this.chart_id = _.uniqueId();
        this.focus_date = moment(new Date());  // main date displayed on the gantt chart
        this.gantt_events = [];
        // The type of the view:
        // gantt = classic gantt view (default)
        // consolidate = values of the first children are consolidated in the gantt's task
        // planning = children are displayed in the gantt's task
        this.type = this.fields_view.arch.attrs.type || 'gantt';

        // Use scale_zoom attribute in xml file to specify zoom timeline (day,week,month,year),
        // by default month.
        var scale = this.fields_view.arch.attrs.scale_zoom;
        if (!_.contains(['day', 'week', 'month', 'year'], scale)) {
            this.scale = "month";
        }

        // gather the fields to get
        var fields_to_gather = [
            "date_start",
            "date_delay",
            "date_stop",
            "consolidation",
            "progress",
            "text",
        ];
        var fields = _.compact(_.map(fields_to_gather, function(key) {
            return self.fields_view.arch.attrs[key] || '';
        }));
        fields.push("name");
        // consolidation exclude, get the related fields
        if (this.fields_view.arch.attrs.consolidation_exclude) {
            fields = fields.concat(this.fields_view.arch.attrs.consolidation_exclude);
        }
        this.fields_to_fetch = fields;  //FIXME: useless?
        // console.log(this.fields_to_fetch);
        // console.log(fields_to_gather);
    },

    on_data_loaded: function (tasks, group_bys, color_by_group) {
        var self = this;

        // Prepare the tasks
        this._super.apply(this, arguments);
        tasks = _.compact(_.map(tasks, function (task) {
            var task_start = time.auto_str_to_date(task[self.fields_view.arch.attrs.date_start]);
            if (!task_start) {
                return false;
            }

            var task_stop;
            var percent;
            if (self.fields_view.arch.attrs.date_stop) {
                task_stop = time.auto_str_to_date(task[self.fields_view.arch.attrs.date_stop]);
                if (!task_stop) {
                    task_stop = moment(task_start).clone().add(1, 'hours');
                }
            } else { // we assume date_duration is defined
                var tmp = formats.format_value(task[self.fields_view.arch.attrs.date_delay],
                                                    self.fields[self.fields_view.arch.attrs.date_delay]);
                if (!tmp) {
                    return false;
                }
                var m_task_start = moment(task_start).add(tmp, gantt.config.duration_unit);
                task_stop = m_task_start.toDate();
            }

            if (_.isNumber(task[self.fields_view.arch.attrs.progress])) {
                percent = task[self.fields_view.arch.attrs.progress] || 0;
            } else {
                percent = 100;
            }

            task.task_start = task_start;
            task.task_stop = task_stop;
            task.percent = percent;

            // Don't add the task that stops before the min_date
            // Usefull if the field date_stop is not defined in the gantt view
            if (self.min_date && task_stop < new Date(self.min_date)) {
                return false;
            }
            
            return task;
        }));
        
        // get the groups
        var split_groups = function(tasks, group_bys) {
            if (group_bys.length === 0) {
                return tasks;
            }
            // Create the group of the first level (with query.group_by())
            // TODO : this code is duplicate with the group created on the other level
            var groups = [];
            for (var g in self.first_groups) {
                var new_g = {tasks: [], __is_group: true,
                             group_start: false, group_stop: false, percent: [],
                             open: true};
                new_g.name = self.first_groups[g].attributes.value;
                new_g.create = [_.first(group_bys), self.first_groups[g].attributes.value];
                // the group color
                var model = self.fields[_.first(group_bys)].relation;
                if (model && _.has(color_by_group, model)) { 
                    new_g.consolidation_color = color_by_group[model][new_g.name[0]];
                }

                // folded or not
                if ((self.fields_view.arch.attrs.fold_last_level && group_bys.length <= 1) || 
                    self.last_contexts.fold_all ||
                    self.type === 'planning') {
                    new_g.open = false;
                }
                        
                groups.push(new_g);
            }
            _.each(tasks, function (task) {
                var group_name = task[_.first(group_bys)];
                var group = _.find(groups, function (group) {
                    return _.isEqual(group.name, group_name);
                });
                if (group === undefined) {
                    // Create the group of the other levels
                    group = {name:group_name, tasks: [], __is_group: true,
                             group_start: false, group_stop: false, percent: [],
                             open: true};
                    
                    // Add the group_by information for creation
                    group.create = [_.first(group_bys), task[_.first(group_bys)]];

                    // folded or not
                    if ((self.fields_view.arch.attrs.fold_last_level && group_bys.length <= 1) || 
                        self.last_contexts.fold_all ||
                        self.type === 'planning') {
                        group.open = false;
                    }

                    // the group color
                    var model = self.fields[_.first(group_bys)].relation;
                    if (model && _.has(color_by_group, model)) { 
                        group.consolidation_color = color_by_group[model][group_name[0]];
                    }
                        
                    groups.push(group);
                }
                if (!group.group_start || group.group_start > task.task_start) {
                    group.group_start = task.task_start;
                }
                if (!group.group_stop || group.group_stop < task.task_stop) {
                    group.group_stop = task.task_stop;
                }
                group.percent.push(task.percent);
                if (self.open_task_id === task.id && self.type !== 'planning') {
                    group.open = true; // Show the just created task
                }
                group.tasks.push(task);
            });
            _.each(groups, function (group) {
                group.tasks = split_groups(group.tasks, _.rest(group_bys));
            });
            return groups;
        };
        var groups = split_groups(tasks, group_bys);

        // If there is no task, add a dummy one
        if (groups.length === 0) {
            groups = [{
                'id': 1,
                'name': '',
                'task_start': self.focus_date,
                'task_stop': self.focus_date,
                'duration': 1,
            }];
        }

        // Creation of the chart
        var gantt_tasks = [];
        var generate_tasks = function(task, level, parent_id) {
            if ((task.__is_group && !task.group_start) || (!task.__is_group && !task.task_start)) {
                return;
            }
            if (task.__is_group) {
                // Only add empty group for the first level
                if (level > 0 && task.tasks.length === 0){
                    return;
                }

                var project_id = _.uniqueId("gantt_project_");
                var group_name = task.name ? formats.format_value(task.name, self.fields[group_bys[level]]) : "-";
                // progress
                var sum = _.reduce(task.percent, function(acc, num) { return acc+num; }, 0);
                var progress = sum / task.percent.length / 100 || 0;
                var t = {
                    'id': project_id,
                    'text': group_name,
                    'is_group': true,
                    'start_date': task.group_start,
                    'duration': gantt.calculateDuration(task.group_start, task.group_stop),
                    'progress': progress,
                    'create': task.create,
                    'open': task.open,
                    'consolidation_color': task.color,
                };
                if (parent_id) { t.parent = parent_id; }
                gantt_tasks.push(t);
                _.each(task.tasks, function(subtask) {
                    generate_tasks(subtask, level+1, project_id);
                });
            }
            else {
                // Consolidation
                // console.log(self.fields_view.arch.attrs);
                // console.log();
                if(self.fields_view.arch.attrs.text!=""){
                    task.name=task[self.fields_view.arch.attrs.text];
                }
                gantt_tasks.push({
                    'id': "gantt_task_" + task.id,
                    'text': task.name,
                    'active': task.active,
                    'start_date': task.task_start,
                    'duration': gantt.calculateDuration(task.task_start, task.task_stop),
                    'progress': task.percent / 100,
                    'parent': parent_id,
                    'consolidation': task[self.fields_view.arch.attrs.consolidation],
                    'consolidation_exclude': task[self.fields_view.arch.attrs.consolidation_exclude],
                    'color': task.color,
                });
            }
        };
        _.each(groups, function(group) { generate_tasks(group, 0); });
        // horrible hack to make sure that something is in the dom with the required id.  The problem is that
        // the view manager render the view in a document fragment. More explaination : GED
        var temp_div_with_id;
        if (this.$div_with_id){
            temp_div_with_id = this.$div_with_id;
        }
        this.$div_with_id = $('<div>').attr('id', this.chart_id);
        this.$div_with_id.wrap('<div></div>');
        this.$div = this.$div_with_id.parent().css({
        });
        this.$div.prependTo(document.body);

        // Initialize the gantt chart
        while (this.gantt_events.length)
            gantt.detachEvent(this.gantt_events.pop());
        self.scale_zoom(self.scale);
        gantt.init(this.chart_id);
        gantt._click.gantt_row = undefined; // Remove the focus on click

        gantt.clearAll();
        gantt.showDate(self.focus_date);
        gantt.parse({"data": gantt_tasks});

        gantt.sort(function(a, b){
            if (gantt.hasChild(a.id) && !gantt.hasChild(b.id)){
                return -1;
            } else if (!gantt.hasChild(a.id) && gantt.hasChild(b.id)) {
                return 1;
            } else {
                return 0;
            }
        });

        // End of horrible hack
        var scroll_state = gantt.getScrollState();
        this.$el.append(this.$div.contents());
        gantt.scrollTo(scroll_state.x, scroll_state.y);
        this.$div.remove();
        if (temp_div_with_id) temp_div_with_id.remove();

        self._configure_gantt_chart(tasks, group_bys, gantt_tasks);
    },




    });

core.view_registry.add('gantt', GanttView);

return GanttView;
});


