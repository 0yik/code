odoo.define('pos_product_categories_color.screen', function (require) {
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

    models.load_fields('pos.category', ['background_color']);

});