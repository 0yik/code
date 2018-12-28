odoo.define('mgm_modifier_sales.mgm_modifier_sales_currency', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');
var SalesTeamDashboardView = require('sales_team.dashboard')

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

SalesTeamDashboardView.include({

    render_monetary_field_int: function(value, currency_id) {
        var currency = session.get_currency(currency_id);
        var digits_precision = currency && currency.digits;
        value = formats.format_value(value || 0, {type: "integer"});
        if (currency) {
            if (currency.position === "after") {
                value += currency.symbol;
            } else {
                value = currency.symbol + value;
            }
        }
        return value;
    },
});


});
