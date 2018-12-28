odoo.define('keywords_search_and', function (require) {
"use strict";

var AutoComplete = require('web.AutoComplete');
var config = require('web.config');
var core = require('web.core');
var data_manager = require('web.data_manager');
var FavoriteMenu = require('web.FavoriteMenu');
var FilterMenu = require('web.FilterMenu');
var GroupByMenu = require('web.GroupByMenu');
var pyeval = require('web.pyeval');
var search_inputs = require('web.search_inputs');
var View = require('web.View');
var SearchView = require('web.SearchView');
var Widget = require('web.Widget');
var local_storage = require('web.local_storage');
var PivotView = require('web.PivotView');
var _t = core._t;
var SearchView = new require('web.SearchView');

var Backbone = window.Backbone;

var FacetValue = Backbone.Model.extend({});

var FacetValues = Backbone.Collection.extend({
    model: FacetValue
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
        this.query = new SearchQuery()
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

    build_search_data: function () {
        var domains = [], contexts = [], groupbys = [];

        this.query.each(function (facet) {
            var field = facet.get('field');
            var domain = field.get_domain(facet);
            if (facet.attributes.category === 'Product'){
                for (var i = 0; i < domain.__domains.length; i++){
                    if (domain.__domains[i].constructor === Array && domain.__domains[i][0] === "|"){
                        domain.__domains[i][0] = "&"
                    }
                }
            }
            if (domain) {
                domains.push(domain);
            }
            var context = field.get_context(facet);
            if (context) {
                contexts.push(context);
            }
            var group_by = field.get_groupby(facet);
            if (group_by) {
                groupbys.push.apply(groupbys, group_by);
            }
        });
        return {
            domains: domains,
            contexts: contexts,
            groupbys: groupbys,
        };
    },
    renderFacets: function (collection, model, options) {
        var self = this;
        var started = [];
        _.invoke(this.input_subviews, 'destroy');
        this.input_subviews = [];

        this.query.each(function (facet) {
            var f = new FacetView(this, facet);
            started.push(f.appendTo(self.$el));
            self.input_subviews.push(f);
        }, this);
        var i = new InputView(this);
        started.push(i.appendTo(self.$el));
        self.input_subviews.push(i);
        _.each(this.input_subviews, function (childView) {
            childView.on('focused', self, self.proxy('childFocused'));
            childView.on('blurred', self, self.proxy('childBlurred'));
        });

        $.when.apply(null, started).then(function () {
            _.last(self.input_subviews).$el.focus();
        });
    },

});
var Facet = Backbone.Model.extend({
    initialize: function (attrs) {
        var values = attrs.values;
        delete attrs.values;

        Backbone.Model.prototype.initialize.apply(this, arguments);

        this.values = new FacetValues(values || []);
        this.values.on('add remove change reset', function (_, options) {
            this.trigger('change', this, options);
        }, this);
    },
    get: function (key) {
        if (key !== 'values') {
            return Backbone.Model.prototype.get.call(this, key);
        }
        return this.values.toJSON();
    },
    set: function (key, value) {
        if (key !== 'values') {
            return Backbone.Model.prototype.set.call(this, key, value);
        }
        this.values.reset(value);
    },
    toJSON: function () {
        var out = {};
        var attrs = this.attributes;
        for(var att in attrs) {
            if (!attrs.hasOwnProperty(att) || att === 'field') {
                continue;
            }
            out[att] = attrs[att];
        }
        out.values = this.values.toJSON();
        return out;
    }
});

var InputView = Widget.extend({
    template: 'SearchView.InputView',
    events: {
        focus: function () { this.trigger('focused', this); },
        blur: function () { this.$el.val(''); this.trigger('blurred', this); },
        keydown: 'onKeydown',
    },
    onKeydown: function (e) {
        switch (e.which) {
            case $.ui.keyCode.BACKSPACE:
                if(this.$el.val() === '') {
                    var preceding = this.getParent().siblingSubview(this, -1);
                    if (preceding && (preceding instanceof FacetView)) {
                        preceding.model.destroy();
                    }
                }
                break;

            case $.ui.keyCode.LEFT: // Stop propagation to parent if not at beginning of input value
                if(this.el.selectionStart > 0) {
                    e.stopPropagation();
                }
                break;

            case $.ui.keyCode.RIGHT: // Stop propagation to parent if not at end of input value
                if(this.el.selectionStart < this.$el.val().length) {
                    e.stopPropagation();
                }
                break;
        }
    }
});

var FacetView = Widget.extend({
     template: 'SearchView.FacetView',
        events: {
        'focus': function () { this.trigger('focused', this); },
        'blur': function () { this.trigger('blurred', this); },
        'click': function (e) {
            if ($(e.target).hasClass('o_facet_remove')) {
                this.model.destroy();
                return false;
            }
            this.$el.focus();
            e.stopPropagation();
        },
        'keydown': function (e) {
            var keys = $.ui.keyCode;
            switch (e.which) {
                case keys.BACKSPACE:
                case keys.DELETE:
                    this.model.destroy();
                    return false;
            }
        }
    },
    init: function (parent, model) {
        this._super(parent);
        this.model = model;
        this.model.on('change', this.model_changed, this);
    },
    destroy: function () {
        this.model.off('change', this.model_changed, this);
        this._super();
    },
    start: function () {
        var self = this;
        var $e = this.$('.o_facet_values').last();
        return $.when(this._super()).then(function () {
            return $.when.apply(null, self.model.values.map(function (value, index) {
                if (index > 0) {
                    if (self.model.attributes.category !== 'Product'){
                        $('<span/>', {html: self.model.get('separator') || _t(" or ")}).addClass('o_facet_values_sep').appendTo($e);
                    }
                }
                return new FacetValueView(self, value).appendTo($e);
            }));
        });
    },
    model_changed: function () {
        this.$el.text(this.$el.text() + '*');
    }

});

var FacetValueView = Widget.extend({
    template: 'SearchView.FacetView.Value',
    init: function (parent, model) {
        this._super(parent);
        this.model = model;
        this.model.on('change', this.model_changed, this);
    },
    destroy: function () {
        this.model.off('change', this.model_changed, this);
        this._super();
    },
    model_changed: function () {
        this.$el.text(this.$el.text() + '*');
    }
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
            if (previous && model.get('category')!=='Product' ) {
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
_.extend(SearchView, {
    SearchQuery: SearchQuery,
    Facet: Facet,
});

});
