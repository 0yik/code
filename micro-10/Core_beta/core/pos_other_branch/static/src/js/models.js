odoo.define('pos_other_branch.pos', function (require) {
"use strict";

var core = require('web.core');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var popups = require('point_of_sale.popups');

var _super_order = models.Order.prototype;
var _t = core._t;

// Load pos configs
models.load_models({
    model: 'pos.config',
    fields: ['name'],
    domain: null,
    loaded: function(self, pos_config) {
        self.pos_configs = pos_config;
    },
});

// Pos order initialize
models.Order = models.Order.extend({
    initialize: function() {
       _super_order.initialize.apply(this,arguments);
       this.branch_selection = false;
    },
   export_as_JSON: function() {
       var json = _super_order.export_as_JSON.apply(this,arguments);
       json.branch_selection = this.get_branch_selection() || false;
       return json;
   },
   init_from_JSON: function(json) {
       _super_order.init_from_JSON.apply(this,arguments);
       this.branch_selection = json.branch_selection || false;
   },
   export_for_printing: function() {
       var json = _super_order.export_for_printing.apply(this,arguments);
       json.branch_selection = this.get_branch_selection() || false;
       return json;
   },
   get_branch_selection: function(){
       return this.branch_selection;
   },
   set_branch_selection: function(branch_id) {
       this.branch_selection = branch_id || false;
       this.trigger('change');
   }
});

// Popup window
var POSPopupWidget = popups.extend({
    template: 'POSPopupWidget',
    show: function(options){
        options = options || {};
        this.other_branch = options.other_branch || [];
        this.value = options.value || false;
        this._super(options);
        this.renderElement();
    },
    click_confirm: function(){
        var value = this.$('#branch_id').val() || false;
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this, value);
        }
    },
});
gui.define_popup({name: 'posbranch', widget: POSPopupWidget});

// Control button
var BranchSelectionButton = screens.ActionButtonWidget.extend({
   template: 'BranchSelectionButton',
   other_branch: function() {
       if (this.pos.get_order()) {
           return this.pos.get_order().branch_selection || false;
       } else {
           return flase;
       };
   },
   button_click: function() {
       var self = this;
       var branch_id = this.pos.get_order().branch_selection || false;
       var other_branch = self.pos.pos_configs;
       this.gui.show_popup('posbranch', {
           'title':  _t('Branch Selection'),
           'other_branch': other_branch,
           'value':  branch_id,
           'confirm': function(value) {
               self.pos.get_order().set_branch_selection(value);
               self.renderElement();
           },
       });
   },
});

screens.define_action_button({
   'name': 'other_branch',
   'widget': BranchSelectionButton,
   'condition': function(){
       return true;
   },
});

});

