odoo.define('manager_function.order_screen', function (require) {
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
            this.$('.manager-button').click(function(){
                self.gui.show_popup('manager_function_widget', {});
            });
        },

    });

    var ManagerFunctionWidget = popups.extend({
        template: 'ManagerFunctionWidget',
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
            this.$('.search-bill-button').click(function() {
                self.gui.show_screen('wk_order', {});
            });

            this.$('.no-sale-button').click(function() {
                self.pos.proxy.open_cashbox();
            });
        },

    });
    gui.define_popup({
        name: 'manager_function_widget',
        widget: ManagerFunctionWidget
    });

});