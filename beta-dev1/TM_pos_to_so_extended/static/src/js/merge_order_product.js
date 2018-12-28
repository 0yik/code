odoo.define('TM_pos_to_so_extended.merge_order_product', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var pos_promotion = require('pos_promotion');
    var ActionManager1 = require('web.ActionManager');
    var PopupWidget = require("point_of_sale.popups");
    var CreateSalesOrder = require("pos_to_sales_order.pos_to_sales_order")
    var gui = require('point_of_sale.gui');
    var QWeb = core.qweb;
    var _t = core._t;
    var promo_popupso = null;

    var _super_orderline = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
			if(this._printed){
				this.destroy();
				return this.pos.get_order().add_product(product, options);
			}
			this.assert_editable();
			options = options || {};
			var attr = JSON.parse(JSON.stringify(product));
			attr.pos = this.pos;
			attr.order = this;
			var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

			if(options.quantity !== undefined){
				line.set_quantity(options.quantity);
			}

			if(options.price !== undefined){
				line.set_unit_price(options.price);
			}

			//To substract from the unit price the included taxes mapped by the fiscal position
			this.fix_tax_included_price(line);

			if(options.discount !== undefined){
				line.set_discount(options.discount);
			}

			if(options.extras !== undefined){
				for (var prop in options.extras) {
					line[prop] = options.extras[prop];
				}
			}

			var merge_orderline = null;
			this.orderlines.models.forEach(function (item) {
				if(item.product.id === line.product.id){
					merge_orderline = item;
				}
            });

			if( merge_orderline && merge_orderline.can_be_merged_with(line) && options.merge !== false){
				merge_orderline.merge(line);
			}else{
				this.orderlines.add(line);
			}
			this.select_orderline(this.get_last_orderline());

			if(line.has_product_lot){
				this.display_lot_popup();
			}
		},
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        can_be_merged_with: function (orderline) {
            var result = _super_orderline.can_be_merged_with.apply(this, arguments);
            if(result || result === undefined){
            	return true;
			}
			return false;
        },
    });
});