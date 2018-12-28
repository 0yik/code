odoo.define("pos_product_list_view.models", function (require) {
    "use strict";
    
    var pos_model = require('point_of_sale.models');
    
    pos_model.load_fields('pos.config',['pos_screen_view']);
    
    
});