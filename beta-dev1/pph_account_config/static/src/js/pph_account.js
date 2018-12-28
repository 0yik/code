odoo.define('pph_account_config.pph_account_config_form', function (require) {
'use strict';
    var session = require('web.session');
    var FormView = require('web.FormView');

     FormView.include({
        load_record: function(record) {
            var self = this;
            console.log('123456');
            self._super.apply(self, arguments);
            if (self.model == 'pph.account.config') {

                setTimeout(function() {
						$('.o_dropdown_toggler_btn.btn.btn-sm.dropdown-toggle').css({"display":"none"});
						$('.o_cp_pager').css({"display":"none"});
					    }, 200);
            }
        },
    });
});