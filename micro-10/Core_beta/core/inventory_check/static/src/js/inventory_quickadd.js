odoo.define('inventory_check.inventory_quickadd', function (require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var ListView = require('web.ListView');
var Model = require('web.DataModel');

var QWeb = core.qweb;

var InventoryQuickAddListView = ListView.extend({
    init: function() {
        var self = this
        this._super.apply(this, arguments);
        if (this.model === 'inventory.check'){
             // $(".o_cp_searchview").hide();
        }
        this.products = [];
        this.current_product = null;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);
        this.defs = [];
        this.defs.push(mod.call("list_products", []).then(function(result) {
            self.products = result;
            mod.call("create_new_product", [0,self.dataset.context]).then(function (result) {
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            })
        }));
    },
    start:function(){
        var tmp = this._super.apply(this, arguments);
        var self = this;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);

        this.$el.parent().prepend(QWeb.render("InventoryCheckQuickAdd", {widget: this}));

        this.$el.parent().find('.oe_account_select_product').change(function () {
            self.current_product = this.value === '' ? 0 : parseInt(this.value);
            mod.call("create_new_product", [self.current_product,self.dataset.context]).then(function (result) {
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            })
        });
        this.defs.push(mod.call("default_get", [['name'],self.dataset.context]).then(function(result) {
            self.current_product = result['name'];
        }));

        return $.when(tmp, this.defs);
    },
    do_search: function(domain, context, group_by) {
        var self = this;
        this.last_domain = domain;
        this.last_context = context;
        this.last_group_by = group_by;
        this.old_search = _.bind(this._super, this);
        var o;
        self.$el.parent().find('.oe_account_select_product').children().remove().end();
        self.$el.parent().find('.oe_account_select_product').append(new Option('Please Select Product', ''));
        for (var i = 0;i < self.products.length;i++){
            o = new Option(self.products[i][1], self.products[i][0]);
            if (self.products[i][0] === self.current_product){
                $(o).attr('selected',true);
                $('#selected_product_id').val(self.current_product);
            }
            self.$el.parent().find('.oe_account_select_product').append(o);
        }
        $(".chosen").chosen();
        return self.search_by_product();
    },
    search_by_product: function() {
        var self = this;
        var domain = [];
        var compound_domain = new data.CompoundDomain(self.last_domain, domain);
        self.dataset.domain = compound_domain.eval();
        return self.old_search(compound_domain, self.last_context, self.last_group_by);
    },
});
core.view_registry.add('tree_inventory_quickadd', InventoryQuickAddListView);
return InventoryQuickAddListView;
});
