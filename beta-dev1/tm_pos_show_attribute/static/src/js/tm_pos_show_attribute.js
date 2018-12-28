odoo.define('tm_pos_show_attribute.tm_pos_show_attribute', function (require) {
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var PosDB = require("point_of_sale.DB");
    var _super_posmodel = models.PosModel.prototype;
    var QWeb = core.qweb;

    models.load_models({
    model: 'product.attribute.value',
    fields: ['id','name'],
    domain: null,
    loaded: function(self,attribute_values){
        self.db.attribute_value = {};
        attribute_values.forEach(function (item) {
            self.db.attribute_value[item.id] = {
                'name': item.name
            };
        });
        console.log(attribute_values);
    }
    });

    models.load_fields('product.product',['attribute_value_ids']);
    screens.ProductListWidget.include({
        init: function(parent, options){
            this._super(parent, options);
            var self = this;
            for (var property in self.pos.db.product_by_id) {
                var name = self.pos.db.product_by_id[property].name;
                self.pos.db.product_by_id[property].attribute_value_ids.forEach(id => {
                    name+= self.pos.db.attribute_value[id] ? " ("+self.pos.db.attribute_value[id].name+")" : "";
                });
                self.pos.db.product_by_id[property].name = name;
                self.pos.db.product_by_id[property].display_name = name;
            }
        }
    });
});
