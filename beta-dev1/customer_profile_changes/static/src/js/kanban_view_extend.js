odoo.define('customer_profile_changes.kanban_view_extend', function (require) {
"use strict";

var KanbanView = require('web_kanban.KanbanView');
var Model = require('web.DataModel');
var core = require('web.core');

KanbanView.include({
    open_record: function (event, options) {
        var self = this;
        if (self.dataset.model === 'res.partner'){
            new Model('res.partner').call(
                    'read', [event.data.id, ['customer_edit_check']]
                ).then(function (results){
                    if (results[0].customer_edit_check === true){
                        alert('This Profile is being edited now');
                        return;
                    }
                    if (self.dataset.select_id(event.data.id)) {
                        self.do_switch_view('form', options);
                    } else {
                        self.do_warn("Kanban: could not find id#" + event.data.id);
                    }
            });
        } else {
            if (self.dataset.select_id(event.data.id)) {
                self.do_switch_view('form', options);
            } else {
                self.do_warn("Kanban: could not find id#" + event.data.id);
            }
        }
    },
});

});