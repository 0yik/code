odoo.define('pos_restaurant.splitbill', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;

var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_quantity_str: function () {
            return parseInt(this.quantityStr).toString() + '   ';
        },
        get_quantity_str_with_unit: function() {
            var unit = this.get_unit();
            if (unit && !unit.is_unit) {
                return parseInt(this.quantityStr).toString() + ' ' + unit.name;
            } else {
                return parseInt(this.quantityStr).toString();
            }
        },
    })
});

