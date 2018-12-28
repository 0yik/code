odoo.define('hilti_modifier_company.hilti_modifier_company', function (require) {
"use strict";

var calenderView = require('web_calendar.CalendarView');
var form_common = require('web.form_common');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
var session = require('web.session');


core.list_widget_registry.map.button.include({
	format: function (row_data, options) {
        options = options || {};
        var attrs = {};
        if (options.process_modifiers !== false) {
            attrs = this.modifiers_for(row_data);
        }
        var template = this.icon && 'ListView.row.button' || 'ListView.row.text_button';
        return QWeb.render(template, {
            widget: this,
            prefix: session.prefix,
            invisible: attrs.invisible || false,
        });
    }
})


var form_widgets = require('web.form_widgets');

	form_widgets.FieldStatus.include({
		render_value: function() {
			var self = this;
			if(self.view.model=='project.booking' || self.view.model=='project.project'){
		        var content = QWeb.render("FieldStatus.content.extended", {
		            'widget': self, 
		            'value_folded': _.find(self.selection.folded, function(i){return i[0] === self.get('value');})
		        });
		        self.$el.html(content);
			}else{
				this._super();
			}
//			if(self.view.model=='project.project'){
//		        var content = QWeb.render("FieldStatus.content.extended", {
//		            'widget': self, 
//		            'value_folded': _.find(self.selection.folded, function(i){return i[0] === self.get('value');})
//		        });
//		        self.$el.html(content);
//			}else{
//				this._super();
//			}
	    }
	})

    calenderView.include({
	    open_quick_create: function(){
		    if (this.model != 'project.booking') {
		        this._super();
		    }
		},
		open_event: function(id, title) {
	        var self = this;
	        if (! this.open_popup_action) {
	            var index = this.dataset.get_id_index(id);
	            this.dataset.index = index;
	            if (this.write_right) {
	                this.do_switch_view('form', { mode: "edit" });
	            } else {
	                this.do_switch_view('form', { mode: "view" });
	            }
	        }
	        else {
	        	if (this.model == 'project.booking') {
	        		new form_common.FormViewDialog(this, {
		                res_model: this.model,
		                res_id: parseInt(id).toString() === id ? parseInt(id) : id,
		                context: this.dataset.get_context(),
		                title: title,
		                view_id: +this.open_popup_action,
		                readonly: true,
		                buttons: [
		                    {text: _t("Close"), close: true}
		                ]
		            }).open();
			    }else{
			    	new form_common.FormViewDialog(this, {
		                res_model: this.model,
		                res_id: parseInt(id).toString() === id ? parseInt(id) : id,
		                context: this.dataset.get_context(),
		                title: title,
		                view_id: +this.open_popup_action,
		                readonly: true,
		                buttons: [
		                    {text: _t("Edit"), classes: 'btn-primary', close: true, click: function() {
		                        self.dataset.index = self.dataset.get_id_index(id);
		                        self.do_switch_view('form', { mode: "edit" });
		                    }},

		                    {text: _t("Delete"), close: true, click: function() {
		                        self.remove_event(id);
		                    }},

		                    {text: _t("Close"), close: true}
		                ]
		            }).open();
			    }
	        }
	        return false;
	    },
	});
});