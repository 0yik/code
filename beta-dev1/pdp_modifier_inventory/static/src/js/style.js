/**
 * Created by telephony on 10/27/17.
 */

odoo.define('beumer_approving_matrix_expense.expense_request', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');
var ListView = require('web.ListView');

var _t = core._t;
var QWeb = core.qweb;

FormView.include({
	do_onchange: function(record) {
		var self = this;
		self._super.apply(self, arguments);
		if (self.model == 'stock.move' && self.fields_view.type == 'tree'){
			self.fields.product_uom_qty.focus();
			$('input[data-fieldname="product_uom_qty"]').focus();
		}
	}
  });

});
