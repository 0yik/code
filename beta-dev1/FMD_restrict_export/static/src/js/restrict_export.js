odoo.define('FMD_restrict_export.restrict_export', function (require) {
"use strict";
	var core = require('web.core');
	var Model = require('web.DataModel');
	var QWeb = core.qweb;
	var _translate = core._t;
	var Sidebar = require('web.Sidebar');

	Sidebar.include({
		add_items: function(section_code, items) {
			var self = this;
			var _super = self._super;
			var args = arguments;
			var model = this.__parentedParent.model

			var Users = new Model('res.users');
			var Values = new Model('ir.values');

   			$.when(
                this.session.user_has_group('fmd_customer.group_audit_partner'),
	            this.session.user_has_group('fmd_customer.group_bd_manager'),
	            this.session.user_has_group('fmd_customer.group_client_general_l3_tax_manager'),
	            this.session.user_has_group('fmd_customer.group_admin_fmd')
            ).done(function(is_audit_partner, is_bd, is_l3_tax, is_admin) {
					if(is_audit_partner || is_bd || is_l3_tax || is_admin){
						_super.apply(self, args);
					}
					else{
						var export_label = _translate("Export"); 
						var new_items = items;
						if (section_code == 'other') {
							new_items = [];
							for (var i = 0; i < items.length; i++) {
								if (items[i]['label'] != export_label) {
									new_items.push(items[i]);
								};
							};
						};
						if (new_items.length > 0) {
							_super.call(self, section_code, new_items);
						};
					}
				});
		},
	});
}
)