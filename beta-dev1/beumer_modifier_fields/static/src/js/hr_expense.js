/**
 * Created by telephony on 10/27/17.
 */

odoo.define('hr_expense.view_hr_expense_sheet_form', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');

var _t = core._t;
var QWeb = core.qweb;

FormView.include({
	load_record: function(record) {
		this._super.apply(this, arguments);
		if (this.model == 'hr.expense.sheet'){
			if (this.get_fields_values().state != 'submit'){
	        	this.$buttons.find('.o_form_button_edit').css({"display":"none"});
	        	console.log('This is my function js first')
	        }
	        else{
	        	this.$buttons.find('.o_form_button_edit').css({"display":""});
	        }
		}
		if (this.model == 'account.invoice'){
			if (this.get_fields_values().state == 'paid'){
	        	this.$buttons.find('.o_form_button_edit').css({"display":"none"});
	        }
	        else{
	        	this.$buttons.find('.o_form_button_edit').css({"display":""});
	        }
		}
		if (this.model == 'purchase.request'){
			if (this.get_fields_values().state == 'to_approve' || this.get_fields_values().state == 'approved'){
	        	this.$buttons.find('.o_form_button_edit').css({"display":"none"});
	        }
	        else{
	        	this.$buttons.find('.o_form_button_edit').css({"display":""});
	        }
		}

	},
    start: function() {
        if (this.$pager) {
            this.$pager.off();
        }
        var self = this;

        this.rendering_engine.set_fields_registry(this.fields_registry);
        this.rendering_engine.set_tags_registry(this.tags_registry);
        this.rendering_engine.set_widgets_registry(this.widgets_registry);
        this.rendering_engine.set_fields_view(this.fields_view);
        this.rendering_engine.render_to(this.$el);

        this.$el.on('mousedown.formBlur', function () {
            self.__clicked_inside = true;
        });

        this.has_been_loaded.resolve();

        // Add bounce effect on button 'Edit' when click on readonly page view.
        this.$(".oe_title,.o_group").on('click', function (e) {
        	if (self.model != 'hr.expense.sheet' && self.model != 'account.invoice' && self.model != 'purchase.request'){
            if(self.get("actual_mode") === "view" && self.$buttons && !$(e.target).is('[data-toggle]')) {
                self.$buttons.find(".o_form_button_edit").openerpBounce();
                core.bus.trigger('click', e);
            }}
        });
        // return this._super();
    },
  });

});
