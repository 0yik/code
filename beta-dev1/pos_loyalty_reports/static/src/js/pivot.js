odoo.define('pos_loyalty_report.pivot', function (require) {
"use strict";
    var core = require('web.core');
    var session = require('web.session');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');
    var PivotView = require('web.PivotView');
    var utils = require('web.utils');
    var _t = core._t;

    PivotView.include({
        prepare_data: function(data, should_update){
            try{
                this._super(data,should_update);
            }catch (error) {
                console.log(error)
            }
        }
    });
});