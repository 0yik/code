odoo.define('inventory_check_bom.bom_check', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var InventoryQuickAddListView = require('inventory_check.inventory_quickadd');

InventoryQuickAddListView.include({
    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.is_check_bom = true;
        this.products = [];
        this.current_product = null;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);
        this.defs = [];
        this.defs.push(mod.call("list_products", []).then(function(result) {
            self.products = result;
            mod.call("create_new_inventory", [0,self.dataset.context]).then(function (result) {
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            })
        }));
    },
    start:function(){
        var tmp = this._super.apply(this, arguments);
        var self = this;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);

        this.$el.parent().find('.oe_account_quickadd').append(QWeb.render("InventoryCheckBOM", {widget: this}));
        this.$el.parent().find('input[type="checkbox"]').change(function (e) {
            self.is_check_bom = $('input[type="checkbox"]').is(':checked');
        });
        this.$el.parent().find('.oe_account_select_product').change(function () {
            self.current_product = this.value === '' ? 0 : parseInt(this.value);
            mod.call("create_new_inventory", [self.current_product, self.is_check_bom, self.dataset.context]).then(function (result) {
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            })
        });
        this.defs.push(mod.call("default_get", [['name'],self.dataset.context]).then(function(result) {
            self.current_product = result['name'];
        }));

        return $.when(tmp, this.defs);
    },
});
});
