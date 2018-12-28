odoo.define('booking_service_V2.web_calendar', function (require) {
    'use strict';
    var core         = require('web.core');
    var form_common  = require('web.form_common');
    var CalendarView = require('web_calendar.CalendarView');

    var _t = core._t;

    CalendarView = CalendarView.extend({
        open_event: function(id, title) {
            console.log('open_event', id, title);

            var self = this;
            if (! this.open_popup_action) {
                var index = this.dataset.get_id_index(id);
                this.dataset.index = index;
                if (this.write_right) {
                    this.do_switch_view('form', { mode: "edit" });
                } else {
                    this.do_switch_view('form', { mode: "view" });
                }
            }
            else {
                new form_common.FormViewDialog(this, {
                    res_model: this.model,
                    res_id: parseInt(id).toString() === id ? parseInt(id) : id,
                    context: this.dataset.get_context(),
                    title: title,
                    view_id: +this.open_popup_action,
                    readonly: true,
                    buttons: [
                        {text: _t("View"), classes: 'btn-primary', close: true, click: function() {
                            self.dataset.index = self.dataset.get_id_index(id);
                            self.do_switch_view('form', { mode: "view" });
                        }},

                        {text: _t("Delete"), close: true, click: function() {
                            self.remove_event(id);
                        }},

                        {text: _t("Close"), close: true}
                    ]
                }).open();
            }
            return false;
        }
    });

    core.view_registry.add('calendar', CalendarView);
    return CalendarView;
});