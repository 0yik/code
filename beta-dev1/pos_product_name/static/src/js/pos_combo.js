odoo.define('pos_product_name.pos_product_name', function (require) {
"use_strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Session = require('web.Session');
    var QWeb = core.qweb;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var _t = core._t;

    models.load_fields('product.product', 'image_exist1');

});
