odoo.define('customer_profile_changes.list_view_extend', function (require) {
"use strict";

var ListView = require('web.ListView');
var Model = require('web.DataModel');
var core = require('web.core');

ListView.include({
    select_record:function (index, view) {
        var self = this;
        var rec_id = self.dataset.ids[index];
        if (self.model === 'res.partner' && rec_id){
            new Model('res.partner').call(
                'read', [rec_id, ['customer_edit_check']]
            ).then(function (results){
                if (results[0].customer_edit_check === true){
                    alert('This Profile is being edited now');
                    return;
                }
                view = view || index === null || index === undefined ? 'form' : 'form';
                self.dataset.index = index;
                _.delay(_.bind(function () {
                    self.do_switch_view(view);
                }, self));
            });
        } else {
            view = view || index === null || index === undefined ? 'form' : 'form';
            self.dataset.index = index;
            _.delay(_.bind(function () {
                self.do_switch_view(view);
            }, self));
        }
    }
});

});
