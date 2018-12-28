odoo.define('max_web_hide_list_view_import.max_web_hide_list_view_import', function (require) {
'use strict';
    var session = require('web.session');
    var ListView = require('web.ListView');

     ListView.include({
        render_buttons: function() {
            var self = this;
            this._super.apply(this, arguments);
            $.when(
    	            this.session.user_has_group('fmd_customer.group_admin_fmd')
                ).done(function(is_admin) {
                	if (is_admin != true && session.uid != 1)
                        if (self.fields_view.model == 'res.partner'){
                            self.$buttons.find('.o_button_import').hide();
                        }
                });
            return this.$buttons;
        },
    });
});
