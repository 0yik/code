odoo.define('report_field_manager.AddRemoveFields', function (require) {
"use strict";

var data_manager = require('web.data_manager');
var search_filters = require('web.search_filters');
var search_inputs = require('web.search_inputs');
var custom_report = require('report_field_manager.custom_report');
var session = require('web.session');
var Model = require('web.DataModel');
var PivotView = require('web.PivotView');
var Widget = require('web.Widget');

return Widget.extend({
    template: 'SearchView.AddRemoveFields',
    events: {
		//'change .o_pivot_extended_prop_field': 'changed',
		'click #ad_rem': function (event) {
			event.preventDefault();
			console.log('okokokok', $(this).parent('.o_dropdown'));
			if ($('.o_apply_fields').parents().find('.o_dropdown').hasClass('open')){
				$('.o_apply_fields').parents().find('.o_dropdown').removeClass('open');
			}
			this.changed();
		},
        'click .o_add_fields': function (event) {
            event.preventDefault();
            this.toggle_custom_fields_menu();
        },
        'click .o_remove_fields': function (event) {
            event.preventDefault();
            this.toggle_custom_fields_menu();
        },
        'click li': function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();
        },
        'hidden.bs.dropdown': function () {
            this.toggle_custom_fields_menu(false);
        },
    },
    init: function (parent, filters) {
        this._super(parent);
        //this.filters = filters || [];
        this.searchview = parent;
        this.propositions = [];
		this.initial_col_groupby = [];
        this.initial_row_groupby = [];
		this.widgets = [];
		this.active_measures = [];
        this.custom_fields_open = false;
		this.model = this.searchview.dataset.model;
		this.dataset = this.searchview.dataset;
	if (this.searchview.ViewManager.views && this.searchview.ViewManager.views['pivot']){
		this.fields_view = this.searchview.ViewManager.views['pivot'].fields_view;
	}else{
		this.fields_view = '';
	}
    },
    start: function () {
        var self = this;
        this.$menu = this.$('.o_filters_menu');
        this.$add_filter = this.$('.o_add_fields');
        this.$apply_filter = this.$('.o_apply_fields');
        this.$add_filds_menu = this.$('.o_add_fields_menu');
        _.each(this.filters, function (group) {
            if (group.is_visible()) {
                group.insertBefore(self.$add_filter);
                $('<li class="divider">').insertBefore(self.$add_filter);
            }
        });
    },
    changed: function() {
		var self = this;
        this.nval = this.$(".o_pivot_extended_prop_field option:selected").text();
		this.nval_val = this.$(".o_pivot_extended_prop_field option:selected").val();
		var pivot = new PivotView(
            this, this.dataset, this.fields_view, {
        });
		pivot.willStart();
    },
    get_fields: function () {
        if (!this._fields_def) {
            this._fields_def = data_manager.load_fields(this.searchview.dataset).then(function (data) {
                var fields = {
                    id: { string: 'ID', type: 'id', searchable: true }
                };
                _.each(data, function(field_def, field_name) {
                    if (field_def.selectable !== false && field_name !== 'id') {
                        fields[field_name] = field_def;
                    }
                });
                return fields;
            });
        }
        return this._fields_def;
    },
    toggle_custom_fields_menu: function (is_open) {
        var self = this;
        this.custom_fields_open = !_.isUndefined(is_open) ? is_open : !this.custom_fields_open;
        var def;
        if (this.custom_fields_open && !this.propositions.length) {
            def = this.append_proposition();
        }
        $.when(def).then(function () {
            self.$add_filter
                .toggleClass('o_closed_menu', !self.custom_fields_open)
                .toggleClass('o_open_menu', self.custom_fields_open);
            self.$add_filds_menu.toggle(self.custom_fields_open);
            self.$('.o_filter_condition').toggle(self.custom_fields_open);
        });
    },
    append_proposition: function () {
        var self = this;
        return this.get_fields().then(function (fields) {
            var prop = new custom_report.ExtendedReportProposition(self, fields);
            self.propositions.push(prop);
            prop.insertBefore(self.$add_filds_menu);
            self.$apply_filter.prop('disabled', false);
            return prop;
        });
    },
    
});

});
