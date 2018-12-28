odoo.define('employee_breaktime.my_attendances', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;


var MyAttendances = Widget.extend({
    events: {
        "click .o_emp_breaktime_sign_in_out_icon": function() {
            this.$('.o_emp_breaktime_sign_in_out_icon').attr("disabled", "disabled");
            this.update_attendance();
        },
    },

    start: function () {
        var self = this;

        var hr_employee = new Model('hr.employee');
        hr_employee.query(['breaktime_state', 'name'])
            .filter([['user_id', '=', self.session.uid]])
            .all()
            .then(function (res) {
                if (_.isEmpty(res) ) {
                    self.$('.o_emp_breaktime_employee').append(_t("Error : Could not find employee linked to user"));
                    return;
                }
                self.employee = res[0];
                self.$el.html(QWeb.render("EmpBreaktimeMyMainMenu", {widget: self}));
            });

        return this._super.apply(this, arguments);
    },

    update_attendance: function () {
        var self = this;
        var hr_employee = new Model('hr.employee');
        hr_employee.call('breaktime_manual', [[self.employee.id], 'employee_breaktime.emp_breaktime_action_my_breaktimes'])
            .then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
    },
});

core.action_registry.add('emp_breaktime_my_breaktimes', MyAttendances);

return MyAttendances;

});
