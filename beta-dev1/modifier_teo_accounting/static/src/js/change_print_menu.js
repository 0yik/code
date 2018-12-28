odoo.define('modifier_teo_accounting.change_print_menu', function (require) {
"use strict";
	var core = require('web.core');
	var Model = require('web.DataModel');
	var QWeb = core.qweb;
	var _translate = core._t;
	var Sidebar = require('web.Sidebar');

	Sidebar.include({
		add_items: function(section_code, items) {
			var self = this;
			console.log("1...........................",this)
			console.log("2...........................",items)
			console.log("3...........................",section_code)
	        if (items) {
	            this.items[section_code].unshift.apply(this.items[section_code],items);
	            this.redraw();
	        }
	    },
	});
}
)