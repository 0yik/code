odoo.define('inventory_check.view_inventory_check_list', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');
var ListView = require('web.ListView');
var View = require('web.View');
var ActionManager = require('web.ActionManager');

var _t = core._t;
var QWeb = core.qweb;

View.include({
     init: function() {
        var self = this;
        this._super.apply(this, arguments);
        if (self.model === 'inventory.check') {
            this.options.selectable = false;
            $(".o_cp_searchview").addClass('importantRuleSearchView');
        }
        else {
            $(".o_cp_searchview").removeClass('importantRuleSearchView');
        }
     }
});
});

