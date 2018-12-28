odoo.define('mail.view_mail_form', function (require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');

    var _t = core._t;
    var QWeb = core.qweb;

    FormView.include({
        load_record: function (record) {
            var self = this;
            self._super.apply(self, arguments);
            if (self.model == 'mail.mail') {
                console.log('abc');
                setTimeout(function() {
									$("button:contains('Discard')").css({"display":"none"});
								}, 100);
                console.log('This is my function js first');
            }
            if (self.model == 'mail.inbox') {
                console.log('abc');
                setTimeout(function() {
									$("button:contains('Discard')").css({"display":"none"});
								}, 100);
                console.log('This is my function js first');
            }
        },
    });

});