odoo.define('pos_scan_IMEI.main', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');


    models.load_models([{
        model: 'stock.production.lot',
        fields: ['id', 'name', 'product_id','imei_number'],
        // domain: function(self){ return [['imei_number','!=',false]];},
        loaded: function(self, serials) {
            self.serial_by_imei_number = {};
            self.serial_by_name = {};
            serials.map(function (item) {
                self.serial_by_imei_number[item.imei_number] = item;
                self.serial_by_name[item.name] = item;
            });
        },
	}]);
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        scan_product: function(parsed_code){
            if (parsed_code.type === 'product'){
                var order = this.get_order();
                var product_id = this.serial_by_imei_number[parsed_code.base_code] ? this.serial_by_imei_number[parsed_code.base_code].product_id[0] : false;
                var product = this.db.product_by_id[product_id];
                if (product){
                    order.add_product(product);
                    return true;
                }
            }
            return _super_posmodel.scan_product.call(this, parsed_code);
        }
    });
});
