openerp.sales_inventory_summary = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.sales_inventory_summary.inventory_summary = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
        },
        start: function () {
            var self = this;
            self.display_data();
        },
        display_data: function () {
            var self = this;
            self.$el.html(QWeb.render("WidgetInventory", {'widget': self.field_manager.dataset.context}));
        },
    });

    instance.web.form.custom_widgets.add('inventory', 'instance.sales_inventory_summary.inventory_summary');
}

odoo.define('sales_inventory_summary.inventory_summary_form_view', function (require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');

    var _t = core._t;
    var QWeb = core.qweb;

    FormView.include({
        load_record: function (record) {
            this._super.apply(this, arguments);
            if (this.model === 'inventory.summary') {
                console.log('dsadasdsa')
                setTimeout(function () {
                    $(".btn btn-primary btn-sm o_form_button_save").css({"display": "none"});
                }, 10);
            }
        },
    });
});