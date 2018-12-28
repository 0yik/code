odoo.define('capture_location.capture_location', function (require) {
"use strict";

    var ControlPanelMixin   = require('web.ControlPanelMixin');
    var core                = require('web.core');
    var time                = require('web.time');
    var ListView            = require('web.ListView');
    var KanbanRecord        = require('web_kanban.Record');
    var KanbanView          = require('web_kanban.KanbanView');
    var Model               = require('web.DataModel');
    var session             = require('web.session');
    var Widget              = require('web.Widget');
    var Signin              = new Model('sign.in');

    var _t = core._t;
    var QWeb = core.qweb;
    var _lt = core._lt;

    KanbanView.include({
        events: {
        'click .button_signin_ex': 'get_location_singin',
        },
        get_location_singin: function(event) {
            var self            = this
            var currentTarget   = event.currentTarget;
            var record_id       = parseInt($(currentTarget).attr("data-id"), 10);
            navigator.geolocation.getCurrentPosition(showPosition);
            function showPosition(position) {
                var value = {'latitude': position.coords.latitude, 'longitude' : position.coords.longitude};
                Signin.call('update_location_signin', [record_id, value], {}).then(function (result) {
                    self.do_reload();
                });
            }
        },
        open_action: function (event) {
            var self = this;
            if (event.data.name === 'sign_out_func'){
                var record_id   = event.target.values.id.value;
                navigator.geolocation.getCurrentPosition(showPosition);
                function showPosition(position) {
                    var value = {'latitude': position.coords.latitude, 'longitude' : position.coords.longitude};
                    Signin.call('update_location_signout', [record_id, value], {}).then(function (result) {
                        self.do_action({
                            name: "History",
                            type: "ir.actions.act_window",
                            views: [[false, "form"]],
                            res_model: "sign_in.history",
                            target: 'new',
                            context: result,
                            view_type : 'form',
                            view_mode : 'form',
                        });
                    });
                }
             }
             return self._super.apply(self, arguments);
        },
    });


});
