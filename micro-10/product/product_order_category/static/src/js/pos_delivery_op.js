// odoo.define('product_order_category.pos_delivery_op', function (require) {
// "use strict";

//     var models = require('point_of_sale.models');
//     var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
//     var SubmitOrderButton = require('pos_restaurant.multiprint');
//     var gui = require('point_of_sale.gui');
//     var DeliveryOptionsPopupWidget = require('delivery_orders_kds.pos_delivery_option');
//     var Model = require('web.DataModel');
//     var _t  = require('web.core')._t;
//     var screens = require('point_of_sale.screens');
//     var pos_model = require('point_of_sale.models');


//     var DeliveryOptionsPopupWidget = DeliveryOptionsPopupWidget.extend({
//         dislay_product_screen: function(){
//             this._super();
//             var self = this.pos;
//             var def = new $.Deferred();
//             var fields = _.find(this.pos.models,function(model){ 
//                 return model.model === 'product.product'; 
//             }).fields;
//             var model = new Model('pos.order.category');
//             self.db.product_by_id = {};
//             self.db.product_by_category_id = {};
//             model.call("get_current_category", ['Delivery',fields]).then(function (result) {
//                 console.log('>>>>>Delivery>>>>>>>>>>',result)
//                 if (result != 0){
//                     if (result == 1){
//                         self.gui.screen_instances['products'].product_list_widget.product_list = [];
//                         self.gui.screen_instances['products'].product_list_widget.renderElement();           
//                         self.db.add_products([]); 
//                     }else{
//                         self.gui.screen_instances['products'].product_list_widget.product_list = result;
//                         self.gui.screen_instances['products'].product_list_widget.renderElement();           
//                         self.db.add_products(result); 
//                     }
//                 }else{
//                     alert("Wrong Product Order Category Defined")
//                 }
//             });
//         },
//     });
//     gui.define_popup({name:'deliveryoptionpopup', widget: DeliveryOptionsPopupWidget});

//     return DeliveryOptionsPopupWidget

// });