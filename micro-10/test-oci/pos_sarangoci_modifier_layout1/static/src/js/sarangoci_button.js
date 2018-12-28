odoo.define('pos_sarangoci_modifier_layout1.floors_extend', function (require) {
"use strict";

    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var floors = require('pos_restaurant.floors');
    var QWeb = core.qweb;
    var _t = core._t;

    var PrioButton = screens.ActionButtonWidget.extend({
        template: 'PrioButton',
        button_click: function() {
            var self = this;
            var user = this.pos.user.id;
            var order = this.pos.get_order();
            var line = this.pos.get_order().get_selected_orderline();
            line.is_priority = true;
            line.trigger("change", line);


        },
    });

    var CancelPrioButton = screens.ActionButtonWidget.extend({
        template: 'CancelPrioButton',
        button_click: function() {
            var self = this;
            var user = this.pos.user.id
            var order = this.pos.get_order();
            var line = this.pos.get_order().get_selected_orderline();
            line.is_priority = false;
            line.trigger("change", line);

        },
    });

    screens.ProductScreenWidget.include({
        start: function(){
            var self = this;
            this._super();
            this.$('.topcenterpane .number-char').click(function(e){
                self.numpad.clickAppendNewChar(e);
            });
            this.$('.topcenterpane .numpad-reset-qty').click(function(e){
                self.numpad.clickResetQty();
            });
            this.$('.note-col').hide();
        },

    });

    screens.NumpadWidget.include({
        start: function() {
            this._super();
            this.$el.find('.numpad-reset-qty').click(_.bind(this.clickResetQty, this));
        },
        clickResetQty: function () {
            return this.state.resetQty();
        }
    });

    screens.OrderWidget.include({
        init: function(parent, options) {
            this._super(parent, options);
            this.numpad_state.bind('reset_quantity', this.reset_quantity, this);
        },
        reset_quantity: function () {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                order.get_selected_orderline().set_quantity(1);
            }
        },
        update_summary: function() {
            this.$('.note-col').hide();
            this._super();

        },
        renderElement: function(scrollbottom) {
            this.$('.note-col').hide();
            this._super(scrollbottom);

        }
    });

    models.NumpadState = models.NumpadState.extend({
		resetQty: function() {
            this.set({ buffer: '' });
            this.trigger('reset_quantity');
		}
	});

    screens.define_action_button({
        'name': 'CancelPrioButton',
        'widget': CancelPrioButton
    });

    screens.define_action_button({
        'name': 'PrioButton',
        'widget': PrioButton
    });





});
