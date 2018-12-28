odoo.define('report_field_manager.CustomFieldReport', function (require) {
"use strict";
var AutoComplete = require('web.AutoComplete');
var config = require('web.config');
var core = require('web.core');
var data_manager = require('web.data_manager');
var FavoriteMenu = require('web.FavoriteMenu');
var FilterMenu = require('web.FilterMenu');
var ReportMenu = require('report_field_manager.AddRemoveFields');
var GroupByMenu = require('web.GroupByMenu');
var pyeval = require('web.pyeval');
var search_inputs = require('web.search_inputs');
var View = require('web.View');
var SearchView = require('web.SearchView');
var Widget = require('web.Widget');
var local_storage = require('web.local_storage');
var PivotView = require('web.PivotView');
var _t = core._t;

var Backbone = window.Backbone;

var FacetValue = Backbone.Model.extend({});

var FacetValues = Backbone.Collection.extend({
    model: FacetValue
});

PivotView.include({
	prepare_fields: function (fields) {
        var self = this,
            groupable_types = ['many2one', 'char', 'boolean', 
                               'selection', 'date', 'datetime', 'integer', 'float', 'monetary'];
        this.fields = fields;
        _.each(fields, function (field, name) {
            if ((name !== 'id') && (field.store === true)) {
                if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                    self.measures[name] = field;
                }
				if (self.ViewManager.nval){
					if (_.contains(groupable_types, field.type)) {
						if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
							if (field.string === self.ViewManager.nval.trim()){
								field['class'] = 'no';
							} else {
								field['class'] = 'yes';
							}
				        } else {
							field['class'] = 'no';
						}
		                self.groupable_fields[name] = field;
		            }
				} else {
		            if (_.contains(groupable_types, field.type)) {
						if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
							field['class'] = 'yes';
				        } else {
							field['class'] = 'no';
						}
		                self.groupable_fields[name] = field;
		            }
				}
            }
        });
        this.measures.__count__ = {string: _t("Count"), type: "integer"};
		//$('.o_pivot_field_menu li').removeClass("custom_fld_hide");
		//self.ViewManager.nval_val
		$('.o_pivot_field_menu li').each(function() {
			if ($(this).attr('data-field') == self.ViewManager.nval_val){
				$(this).removeClass("custom_fld_hide");
			}
		});
		//console.log('yoyoyyoyyoyo', $('.o_pivot_field_menu li'));
    },
});


SearchView.include({
    init: function() {
        this._super.apply(this, arguments);
        this.query = undefined;
        this.title = this.options.action && this.options.action.name;
        this.action_id = this.options.action && this.options.action.id;
        this.search_fields = [];
        this.filters = [];
        this.groupbys = [];
        this.visible_filters = (local_storage.getItem('visible_search_menu') === 'true');
        this.input_subviews = []; // for user input in searchbar
        this.search_defaults = this.options.search_defaults || {};
        this.headless = this.options.hidden &&  _.isEmpty(this.search_defaults);
        this.$buttons = this.options.$buttons;

        this.filter_menu = undefined;
        this.groupby_menu = undefined;
        this.favorite_menu = undefined;
        this.addremove_menu = undefined;//Kunal
    },
    start: function() {
        if (this.headless) {
            this.do_hide();
        }
        this.toggle_visibility(false);
        this.setup_global_completion();
        this.query = new SearchView.SearchQuery()
                .on('add change reset remove', this.proxy('do_search'))
                .on('change', this.proxy('renderChangedFacets'))
                .on('add reset remove', this.proxy('renderFacets'));
        this.$('.o_searchview_more')
            .toggleClass('fa-search-minus', this.visible_filters)
            .toggleClass('fa-search-plus', !this.visible_filters);
        var menu_defs = [];
        this.prepare_search_inputs();
        if (this.$buttons) {
            if (!this.options.disable_filters) {
                this.filter_menu = new FilterMenu(this, this.filters);
                menu_defs.push(this.filter_menu.appendTo(this.$buttons));
                //Kunal
                this.addremove_menu = new ReportMenu(this, this.filters);
                menu_defs.push(this.addremove_menu.appendTo(this.$buttons));
            }
            if (!this.options.disable_groupby) {
                this.groupby_menu = new GroupByMenu(this, this.groupbys);
                menu_defs.push(this.groupby_menu.appendTo(this.$buttons));
            }
            if (!this.options.disable_favorites) {
                this.favorite_menu = new FavoriteMenu(this, this.query, this.dataset.model, this.action_id, this.favorite_filters);
                menu_defs.push(this.favorite_menu.appendTo(this.$buttons));
            }
        }
        return $.when.apply($, menu_defs).then(this.set_default_filters.bind(this));
    },
});

var SearchQuery = Backbone.Collection.extend({
    model: Facet,
    initialize: function () {
        Backbone.Collection.prototype.initialize.apply(
            this, arguments);
        this.on('change', function (facet) {
            if(!facet.values.isEmpty()) { return; }

            this.remove(facet, {silent: true});
        }, this);
        alert("Global");
    },
    add: function (values, options) {
        options = options || {};

        if (!values) {
            values = [];
        } else if (!(values instanceof Array)) {
            values = [values];
        }

        _(values).each(function (value) {
            var model = this._prepareModel(value, options);
            var previous = this.detect(function (facet) {
                return facet.get('category') === model.get('category') &&
                       facet.get('field') === model.get('field');
            });
            if (previous) {
                previous.values.add(model.get('values'), _.omit(options, 'at', 'merge'));
                return;
            }
            Backbone.Collection.prototype.add.call(this, model, options);
        }, this);
        // warning: in backbone 1.0+ add is supposed to return the added models,
        // but here toggle may delegate to add and return its value directly.
        // return value of neither seems actually used but should be tested
        // before change, probably
        return this;
    },
    toggle: function (value, options) {
        options = options || {};

        var facet = this.detect(function (facet) {
            return facet.get('category') === value.category
                && facet.get('field') === value.field;
        });
        if (!facet) {
            return this.add(value, options);
        }

        var changed = false;
        _(value.values).each(function (val) {
            var already_value = facet.values.detect(function (v) {
                return v.get('value') === val.value
                    && v.get('label') === val.label;
            });
            // toggle value
            if (already_value) {
                facet.values.remove(already_value, {silent: true});
            } else {
                facet.values.add(val, {silent: true});
            }
            changed = true;
        });
        // "Commit" changes to values array as a single call, so observers of
        // change event don't get misled by intermediate incomplete toggling
        // states
        facet.trigger('change', facet);
        return this;
    }
});

});
