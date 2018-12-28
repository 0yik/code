odoo.define('email_management', function (require) {
    "use strict";
    var Chatter = require('mail.Chatter');
    var core = require('web.core');
    var form_common = require('web.form_common');
    var Model = require('web.Model');
    var ListView = require('web.ListView');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var ComposeMail = Chatter.include({
        on_open_composer_new_message: function () {
            var self = this;
            var res_id = self.res_id;
            var model = self.view.model;
            new Model("ir.model.data").call("get_object_reference", ['email_management', 'pop_up_compose_mail'])
                .then(function (result) {
                    var xml_id = false;
                    xml_id = result[1];
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'mail.inbox',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[xml_id, 'form']],
                        target: 'new',
                        domain: [],
                        context: {
                            'button_message_res_id': res_id,
                            'button_message_model': model,
                            'default_model': model,
                            'default_res_id': res_id,
                        },
                    })
                });
        }
    });

    function action_refresh_mail() {
        var self = this;
        console.log('clicked');
        var uid = this.session.uid;
        new Model("res.users").call("read", [uid, ['incomming_mail_server']]).then(function (incomming_id) {
            if (incomming_id[0].incomming_mail_server[0]) {
                new Model("fetchmail.server.inbox").call("fetch_mail", [incomming_id[0].incomming_mail_server[0]]).then(function (result) {
                    return self.reload();
                });
            }

        });

    }

    var ListView = ListView.include({
        render_buttons: function () {
            var self = this;
            var add_button = false;
            if (!this.$buttons) { // Ensures that this is only done once
                add_button = true;
            }
            this._super.apply(this, arguments); // Sets this.$buttons
            if (add_button) {
                this.$buttons.on('click', '.o_list_button_mail_refresh', action_refresh_mail.bind(this));
            }
        }
    });
});