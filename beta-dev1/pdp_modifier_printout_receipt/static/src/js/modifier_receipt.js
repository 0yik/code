odoo.define('pdp_modifier_printout_receipt.modifier_receipt', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var utils = require('web.utils');

var round_pr = utils.round_precision;
var QWeb     = core.qweb;

models.load_fields('res.company','street');
models.load_fields('res.company','street2');
models.load_fields('res.company','city');
models.load_fields('res.company','state_id');
models.load_fields('res.company','country_id');
models.load_fields('res.company','zip');
models.load_fields('res.company','vat');

});
