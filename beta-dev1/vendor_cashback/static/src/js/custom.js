odoo.define('vendor_cashback.Custom', function (require) {
"use strict";

var core = require('web.core');
var list_widget_registry = core.list_widget_registry;
var ListView = require('web.ListView');
var Column = ListView.Column;
var ColumnBoolean = Column.ColumnBoolean;

var ColumnBoolean = Column.extend({
    _format: function (row_data, options) {
        var order_type = ["Sales Order", "POS"];
        if(row_data && row_data.is_sale_order && row_data.is_sale_order.value && order_type.includes(row_data.is_sale_order.value) ){
            var value = row_data[this.id].value;
            if (value && this.password === 'True') {
                return value.replace(/[\s\S]/g, _.escape(this.replacement));
            }
            return this._super(row_data, options);
        }
        return _.str.sprintf('<div class="o_checkbox"><input type="checkbox" %s disabled="disabled"/><span/></div>',
                 row_data[this.id].value ? 'checked="checked"' : '');
    }
});

list_widget_registry
    .add('field.boolean', ColumnBoolean);

});
