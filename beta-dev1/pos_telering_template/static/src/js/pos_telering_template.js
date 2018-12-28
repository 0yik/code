odoo.define('pos_telering_template.main', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var pos_product_template = require('pos_product_template.pos_product_template');


    var PosDB = require("point_of_sale.DB");
    PosDB.include({
        add_templates: function(templates){
            for(var i=0 ; i < templates.length; i++){
                var attribute_value_ids = [];
                // store Templates
                this.template_by_id[templates[i].id] = templates[i];

                // Update Product information
                for (var j = 0; j <templates[i].product_variant_ids.length; j++){
                    var product = this.product_by_id[templates[i].product_variant_ids[j]];
                    if(!product)continue;
                    for (var k = 0; k < product.attribute_value_ids.length; k++){
                        if (attribute_value_ids.indexOf(product.attribute_value_ids[k])==-1){
                            attribute_value_ids.push(product.attribute_value_ids[k]);
                        }
                    }
                    product.product_variant_count = templates[i].product_variant_count;
                    product.is_primary_variant = (j==0);
                }
                this.template_by_id[templates[i].id].attribute_value_ids = attribute_value_ids;
            }
        },
    });
});
