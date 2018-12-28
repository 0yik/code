odoo.define('hashmicro_modifier_fields_meeting.CalendarViewChange', function (require) {
"use strict";
/*---------------------------------------------------------
 * OpenERP web_calendar
 *---------------------------------------------------------*/

var core = require('web.core');
var data = require('web.data');
var form_common = require('web.form_common');
var formats = require('web.formats');
var Model = require('web.DataModel');
var time = require('web.time');
var utils = require('web.utils');
var View = require('web.View');
var local_storage = require('web.local_storage');
var CalendarView = require('web_calendar.CalendarView');

    CalendarView.include({
            open_event: function(id, title) {
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
                var res_id = parseInt(id).toString() === id ? parseInt(id) : id;
                new form_common.FormViewDialog(this, {
                    res_model: this.model,
                    res_id: res_id,
                    context: this.dataset.get_context(),
                    title: title,
                    view_id: +this.open_popup_action,
                    readonly: true,
                    buttons: [
                        {text: ("Edit"), classes: 'btn-primary', close: true, click: function() {
                            self.dataset.index = self.dataset.get_id_index(id);
                            self.do_switch_view('form', { mode: "edit" });
                        }},

    //                    {text: _t("Delete"), close: true, click: function() {
    //                        self.remove_event(res_id);
    //                    }},

                        {text: ("Close"), close: true}
                    ]
                }).open();
            }
            return false;
        },
            });

            });