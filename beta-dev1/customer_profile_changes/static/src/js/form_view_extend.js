odoo.define('customer_profile_changes.form_view_extend', function (require) {
"use strict";

var FormView = require('web.FormView');
var Model = require('web.DataModel');
var core = require('web.core');

FormView.include({
    on_button_edit: function() {
        var self = this;
        // Here we are calling odoo method to lock the record
        if (self.model === 'res.partner'){
            new Model('res.partner').call(
                'action_edit', [self.datarecord.id]
            ).then(function (results) {
                return self.to_edit_mode();
            });
        }
        else{
            return this.to_edit_mode();
        }
    },
    on_button_save: function() {
        var self = this;
        // Here we are calling odoo method to unlock the record while saving
        if (self.model === 'res.partner'){
            new Model('res.partner').call(
                'action_save', [self.datarecord.id]
            );
        };
        if (this.is_disabled) {
            return;
        }
        this.disable_button();
        return this.save().then(function(result) {
            self.trigger("save", result);
            return self.reload().then(function() {
                self.to_view_mode();
                core.bus.trigger('do_reload_needaction');
                core.bus.trigger('form_view_saved', self);
            }).always(function() {
                self.enable_button();
            });
        }).fail(function(){
            self.enable_button();
        });
    },
    on_button_cancel: function() {
        var self = this;
        if (self.model === 'res.partner'){
            new Model('res.partner').call(
                'action_discard', [self.datarecord.id]
            );
        };
        this.can_be_discarded().then(function() {
            if (self.get('actual_mode') === 'create') {
                self.trigger('history_back');
            } else {
                self.to_view_mode();
                $.when.apply(null, self.render_value_defs).then(function(){
                    self.trigger('load_record', self.datarecord);
                });
            }
        });
        this.trigger('on_button_cancel');
        return false;
    }
});

});
