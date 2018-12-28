odoo.define('hilti_modifier_tester_myrequests.hilti_modifier_tester_myrequests', function (require) {
"use strict";

var form_common = require('web.form_common');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;

var form_widgets = require('web.form_widgets');

	form_widgets.FieldStatus.include({
		render_value: function() {
			var self = this;
			if(self.view.model=='my.request'){
		        var content = QWeb.render("FieldStatus.content.extended", {
		            'widget': self, 
		            'value_folded': _.find(self.selection.folded, function(i){return i[0] === self.get('value');})
		        });
		        self.$el.html(content);
			}else{
				this._super();
			}
	    }
	})

});