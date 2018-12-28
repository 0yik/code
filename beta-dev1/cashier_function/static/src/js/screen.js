odoo.define('cashier_function.order_screen', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var core = require('web.core');
    var _t = core._t;
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');

    screens.ProductScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.cashier-button').click(function(){
                self.gui.show_popup('cashier_function_widget', {});
            });
        },

    });

    var CashierFunctionWidget = popups.extend({
        template: 'CashierFunctionWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        show: function(options) {
            var self = this;
            this._super(options);

        },
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var selectedOrder = self.pos.get('selectedOrder');
            this.$('.split-button').click(function() {
                if(self.pos.get_order().get_orderlines().length > 0){
                    self.gui.show_screen('splitbill');
                }
            });
        },

    });
    gui.define_popup({
        name: 'cashier_function_widget',
        widget: CashierFunctionWidget
    });
});