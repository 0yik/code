odoo.define('inventory_check_bom.bom_check', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var InventoryQuickAddListView = require('inventory_check.inventory_quickadd');
var ajax = require('web.ajax');
var store_product_id;
InventoryQuickAddListView.include({
    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.is_check_bom = true;
        this.products = [];
        this.current_product = null;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);
        this.defs = [];
        var qty = 0;
        this.defs.push(mod.call("list_products", []).then(function(result) {
            mod.call("create_new_inventory", [0,qty,self.dataset.context]).then(function (result) {
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            })
        }));
    },
    start:function(){
        var tmp = this._super.apply(this, arguments);
        var self = this;
        var qty = 0;
        var mod = new Model("inventory.check", self.dataset.context, self.dataset.domain);
        this.$el.parent().find('.oe_account_quickadd').append(QWeb.render("InventoryCheckBOM", {widget: this}));
        this.$el.parent().find('input[type="checkbox"]').change(function (e) {
            self.is_check_bom = $('input[type="checkbox"]').is(':checked');
        });
        this.$el.parent().find('#max_qty').click(function (e) {
            e.preventDefault();
//            self.current_product = self.$el.parent().find('.oe_account_select_product option:selected').val();
            self.current_product = $('#selected_product_id').val();
            if (self.current_product == 0){
                alert('Please select a product');
            }
            else{
                store_product_id = self.current_product;
                mod.call("find_max_qty_product", [self.current_product]).then(function (result) {
                    self.$el.parent().find('#product_qty').val(result);
                })
            }
            ajax.jsonRpc('/get_product_details', 'call', {
                'product_id': self.current_product === '' ? 0 : parseInt(self.current_product),
            }).then(function (submit) {
                qty = self.$el.parent().find('#product_qty').val();
                self.$el.parent().find('#product_uom').remove();
                if (submit[1] != false){
                    self.$el.parent().find('#product_qty').after('<span id="product_uom" style="font-size: 16px; margin-right: 30px;">'+ submit[1] +'</span>')
                }
                mod.call("create_new_inventory", [qty,self.current_product,self.is_check_bom]).then(function (result) {
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                    self.$el.parent().find('.oe_account_select_product option:eq("'+self.current_product+'")').prop('selected', true);
                })
            });
        });
        this.$el.parent().find('#product_qty').change(function() {
//            self.current_product = self.$el.parent().find('.oe_account_select_product option:selected').val();
            self.current_product = $('#selected_product_id').val();
            if (self.current_product == 0){
                self.current_product = store_product_id
            }
            else{
                store_product_id = self.current_product;
            }
            ajax.jsonRpc('/get_product_details', 'call', {
                'product_id': self.current_product === '' ? 0 : parseInt(self.current_product),
            }).then(function (submit) {
                qty = self.$el.parent().find('#product_qty').val();
                self.$el.parent().find('#product_uom').remove();
                if (submit[1] != false){
                    self.$el.parent().find('#product_qty').after('<span id="product_uom" style="font-size: 16px; margin-right: 30px;">'+ submit[1] +'</span>')
                }
                mod.call("create_new_inventory", [qty,self.current_product,self.is_check_bom]).then(function (result) {
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                    self.$el.parent().find('.oe_account_select_product option:eq("'+self.current_product+'")').prop('selected', true);
                })
            });
        });

        this.$el.parent().find('.oe_account_bom_check').change(function () {
//            self.current_product = self.$el.parent().find('.oe_account_select_product option:selected').val();
            self.current_product = $('#selected_product_id').val();
            if (self.current_product == 0){
                self.current_product = store_product_id
            }
            else{
                store_product_id = self.current_product;
            }
            ajax.jsonRpc('/get_product_details', 'call', {
                'product_id': self.current_product === '' ? 0 : parseInt(self.current_product),
            }).then(function (submit) {
                qty = self.$el.parent().find('#product_qty').val();
                self.$el.parent().find('#product_uom').remove();
                if (submit[1] != false){
                    self.$el.parent().find('#product_qty').after('<span id="product_uom" style="font-size: 16px; margin-right: 30px;">'+ submit[1] +'</span>')
                }
                mod.call("create_new_inventory", [qty,self.current_product,self.is_check_bom]).then(function (result) {
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                    self.$el.parent().find('.oe_account_select_product option:eq("'+self.current_product+'")').prop('selected', true);
                })
            });
        });

        this.$el.parent().find('.oe_account_select_product').change(function () {
            self.current_product = this.value === '' ? 0 : parseInt(this.value);
            ajax.jsonRpc('/get_product_details', 'call', {
                'product_id': self.current_product,
            }).then(function (submit) {
                self.$el.parent().find('#product_qty').val(0);
                qty = self.$el.parent().find('#product_qty').val();
                self.$el.parent().find('#product_uom').remove();
                if (submit[1] != false){
                    self.$el.parent().find('#product_qty').after('<span id="product_uom" style="font-size: 16px; margin-right: 30px;">'+ submit[1] +'</span>')
                }
                mod.call("create_new_inventory", [qty,self.current_product,self.is_check_bom]).then(function (result) {
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                })
            });
        });

        this.defs.push(mod.call("default_get", [['name'],self.dataset.context]).then(function(result) {
            self.current_product = result['name'];
        }));
        // var myTimer = setInterval(function(){
        //     $(".chosen").chosen();
        // },100);
        return $.when(tmp, this.defs);
    },

});




});
