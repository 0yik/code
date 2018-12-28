
odoo.define("hr_gps_attendance_new.get_current_location_new", function (require) {
    "use strict";

    var form_widget = require('web.form_widgets');
    var Model = require('web.Model');

    var MyAttendanceswidget = require('hr_attendance.my_attendances');
    var Widget = require('web.Widget');

    MyAttendanceswidget.include({

    update_attendance: function () {
            var self = this;
            var a = this._super
            var hr_employee = new Model('hr.employee');
            console.log('before superrrrrr');

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {

                    hr_employee.call('check_in_out_radius', [position.coords.latitude, position.coords.longitude, self.employee.id])
                        .then(function(result) {
                        if (result.check) {
//                            a(self)
                            hr_employee.call('attendance_manual', [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'])
                                .then(function(result) {
                                    if (result.action) {
                                        self.do_action(result.action);
                                        if (navigator.geolocation) {
                                            navigator.geolocation.getCurrentPosition(function(position) {
                                                var custom_model = new Model('hr.attendance');
                                                custom_model.call('get_sign_in_out_location',[position.coords.latitude, position.coords.longitude, result.action.attendance.id])
                                            },function errorFunction(err) {
                                                alert("Allow get location to this site and check application is running on Secure Server?\n As Geolocation is support only Secure Server");
                                            });
                                        }
                                    } else if (result.warning) {
                                        self.do_warn(result.warning);
                                    }
                                });
                        }else{
                            if (result.attendance_state == 'in') {
                                alert('The check in location is out of boundary. Please check in again later!')
                            }else{
                                alert('The check out location is out of boundary. Please check out again later!')
                            }
                            return false;
                        }
                });
                },function errorFunction(err) {
                    alert("Allow get location to this site and check application is running on Secure Server?\n As Geolocation is support only Secure Server");
                });
            }
//            this._super()
        },

    });

});