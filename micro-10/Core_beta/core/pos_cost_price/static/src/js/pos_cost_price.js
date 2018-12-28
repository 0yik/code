odoo.define('pos_cost_price.pos_cost_price', function (require) {
"use strict";
	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var utils = require('web.utils');
	var PopupWidget = require('point_of_sale.popups');
	var DB = require('point_of_sale.DB');
	var formats = require('web.formats');
	var Model = require('web.DataModel');
	var PosBaseWidget = require('point_of_sale.BaseWidget');
	var _initialize_orderline_ = models.Orderline.prototype;
	var round_di = utils.round_decimals;

	var QWeb = core.qweb;
	var _t = core._t;
	
	var _super_posmodel = models.PosModel.prototype;
	
	models.load_fields("product.product", ['standard_price']);
});