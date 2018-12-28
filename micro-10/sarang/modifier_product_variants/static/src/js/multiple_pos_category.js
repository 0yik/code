odoo.define('multiple_pos_category', function (require) {
"use strict";
	var Model = require('web.DataModel');
	var models = require('point_of_sale.models');
	models.load_fields('product.product', 'pos_categ_ids');
});