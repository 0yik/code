odoo.define('delivery_orders_kds.payment_plan', function (require) {
"use strict";

    var core = require('web.core');
    var models = require('point_of_sale.models');

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var _t = core._t;
    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            this.payment_plan = {};
            $('.paymentplan_btn span').text('');
            Order.initialize.apply(this, arguments);
        },
        set_payment_plan: function (payment_plan) {
            this.payment_plan = payment_plan || {};
        },
        get_payment_plan: function () {
            return this.payment_plan;
        },
        change_payment_plan: function () {
            $('.paymentplan_btn span').text('(' + this.payment_plan.name + ')');
        }
    });

    var PaymentPlanButton = screens.ActionButtonWidget.extend({
        'template': 'PaymentPlanButton',
        button_click: function(){
            this.gui.show_popup('payment_plan_popup', {
                'title': _t("CHOOSE PAYMENT PLAN"),
                'parent': this,
            });
        },
        get_select_payment_plan: function () {
            return this.pos.get_order() && this.pos.get_order().get_payment_plan() || {};
        },
    });

    screens.define_action_button({
        'name': 'payment_plan_action',
        'widget': PaymentPlanButton,
        'condition': function() {
            return true;
        },
    });

    models.load_fields('account.journal', ['name', 'code']);

    var PaymentPlanPopupWidget = PopupWidget.extend({
        template: 'PaymentPlanPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {

        }),
        init: function(parent, options){
            this._super(parent, options);
            this.parent_widget = false;
            this.journals = this.pos.journals;
        },
        show: function(options){
            options = options || {};
            this._super(options);
            this.parent_widget = options.parent || false;
        },
        click_confirm: function(){
            var method_id = $('select.payment_plan_selection').val();
            var method = _.first(_.filter(this.journals, function (journal){
                return journal.id == method_id;
            }))
            this.pos.get_order().set_payment_plan(method);
            this.pos.get_order().change_payment_plan();
            this.gui.close_popup();
        },
    });

    gui.define_popup({name:'payment_plan_popup', widget: PaymentPlanPopupWidget})
    return PaymentPlanButton;
});

