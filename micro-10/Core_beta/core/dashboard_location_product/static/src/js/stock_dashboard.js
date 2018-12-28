odoo.define('dashboard_location_product', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var Model = require('web.Model');
var session = require('web.session');
var PlannerCommon = require('web.planner.common');
var framework = require('web.framework');
var webclient = require('web.web_client');
var PlannerDialog = PlannerCommon.PlannerDialog;

var QWeb = core.qweb;
var _t = core._t;

var StockDashboard = Widget.extend({
    template: 'StockDashboardMain',

    init: function(parent, data){
        this.all_dashboards = ['1','2','3','4','5','6','7','8'];
        return this._super.apply(this, arguments);
    },

    start: function(){
        return this.load(this.all_dashboards);
    },

    load: function(dashboards){
        var self = this;
        var loading_done = new $.Deferred();
        session.rpc("/dashboard_location_product/data", {}).then(function (data) {
            // Load each dashboard
            var all_dashboards_defs = [];
            _.each(dashboards, function(dashboard) {
                var dashboard_def = self['location_product_' + dashboard](data);
                if (dashboard_def) {
                    all_dashboards_defs.push(dashboard_def);
                }
            });

            // Resolve loading_done when all dashboards defs are resolved
            $.when.apply($, all_dashboards_defs).then(function() {
                loading_done.resolve();
            });
        });
        return loading_done;
    },

    location_product_1: function(data){
        return new StockDashboard1(this, data.location_product_1).replace(this.$('.o_dashboard_location_product_1'));
    },

    location_product_2: function(data){
        return new StockDashboard2(this, data.location_product_2).replace(this.$('.o_dashboard_location_product_2'));
    },

    location_product_3: function(data){
        return new StockDashboard3(this, data.location_product_3).replace(this.$('.o_dashboard_location_product_3'));
    },

    location_product_4: function(data){
        return new StockDashboard4(this, data.location_product_4).replace(this.$('.o_dashboard_location_product_4'));
    },

    location_product_5: function(data){
        return new StockDashboard5(this, data.location_product_5).replace(this.$('.o_dashboard_location_product_5'));
    },

    location_product_6: function(data){
        return new StockDashboard6(this, data.location_product_6).replace(this.$('.o_dashboard_location_product_6'));
    },

    location_product_7: function(data){
        return new StockDashboard7(this, data.location_product_7).replace(this.$('.o_dashboard_location_product_7'));
    },

    location_product_8: function(data){
        return new StockDashboard8(this, data.location_product_8).replace(this.$('.o_dashboard_location_product_8'));
    },

});

var StockDashboard1 = Widget.extend({

    template: 'StockDashboard1',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard2 = Widget.extend({
    template: 'StockDashboard2',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard3 = Widget.extend({

    template: 'StockDashboard3',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard4 = Widget.extend({

    template: 'StockDashboard4',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard5 = Widget.extend({

    template: 'StockDashboard5',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard6 = Widget.extend({

    template: 'StockDashboard6',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard7 = Widget.extend({

    template: 'StockDashboard7',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

var StockDashboard8 = Widget.extend({

    template: 'StockDashboard8',

    events: {
        'click .o_open_location': 'on_open_location',
        'click .o_open_products': 'on_open_products',
    },

    init: function(parent, data){
        this.data = data;
        this.location_id = data.id;
        this.name = data.name;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    start: function() {
        this._super.apply(this, arguments);
        if (odoo.db_info && _.last(odoo.db_info.server_version_info) !== 'e') {
            $(QWeb.render("DashboardEnterprise")).appendTo(this.$el);
        }
    },

    on_open_products: function(){
        this.do_action({
            name: this.name + ' - Current Stock',
            res_model: 'stock.quant',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            view_mode: 'form',
            target: 'current',
            domain: [['location_id', 'child_of', [this.location_id]]],
            context: {search_default_internal_loc: 1, search_default_productgroup: 1, active_id: this.location_id, active_ids: [this.location_id], location_id: this.location_id},
        });
    },

    on_open_location: function(){
        this.do_action({
            name: this.name,
            res_model: 'stock.location',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'current',
            res_id: this.location_id,
        });
    },

});

core.action_registry.add('dashboard_location_product.main', StockDashboard);

return {
    StockDashboard: StockDashboard,
    StockDashboard1: StockDashboard1,
    StockDashboard2: StockDashboard2,
    StockDashboard3: StockDashboard3,
    StockDashboard4: StockDashboard4,
    StockDashboard5: StockDashboard5,
    StockDashboard6: StockDashboard6,
    StockDashboard7: StockDashboard7,
    StockDashboard8: StockDashboard8,
};

});
