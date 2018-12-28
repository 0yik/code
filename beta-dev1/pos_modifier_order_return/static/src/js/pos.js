odoo.define('pos_modifier_order_return.pos', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var pos_orders = require('pos_orders.pos_orders');

    var floors_screen = null
    for (var index in gui.Gui.prototype.screen_classes) {
        if(gui.Gui.prototype.screen_classes[index].name=='floors'){
            floors_screen =gui.Gui.prototype.screen_classes[index].widget 
            gui.Gui.prototype.screen_classes.splice(index, 1);
        }
    }
    var FloorScreenWidget = floors_screen.extend({
        show: function(){
            var self = this;
            this._super();
            $('#cancel_refund_order').hide();
        }
    });
    gui.define_screen({
        'name': 'floors',
        'widget': FloorScreenWidget,
        'condition': function(){
        return this.pos.config.iface_floorplan;
        },  
    });

    var SuperPosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        set_order: function(order){
            SuperPosModel.set_order.call(this,order);
            if((order != null && !order.is_return_order) || order == null){
                $("#cancel_refund_order").hide();
            }
            else{
                $("#cancel_refund_order").show();
            }
        },
    });

    // add pin for supervisor
    pos_orders.include({
        display_order_details: function(visibility, order, clickpos) {
			var self = this;
			self._super(visibility, order, clickpos);
            self.$("#wk_refund").off().on("click", function() {
                self.gui.show_popup('pin_number',{
                    'after_certain':function(){
                        self.wk_refuld_click(order);
                        self.gui.popup_instances.return_products_popup.$('.button.cancel').show();
                    },
                });
            });
		},
        wk_refuld_click:function (order) {
            var self = this;
            var order_list = self.pos.db.pos_all_orders;
            var order_line_data = self.pos.db.pos_all_order_lines;
            var order_id = this.id;
            var message = '';
            var non_returnable_products = false;
            var original_orderlines = [];
            var allow_return = true;
            if(order.return_status == 'Fully-Returned'){
                message = 'No items are left to return for this order!!'
                allow_return = false;
            }
            if (allow_return) {
                order.lines.forEach(function(line_id){
                    var line = self.pos.db.line_by_id[line_id];
                    var product = self.pos.db.get_product_by_id(line.product_id[0]);
                    if(product == null){
                        non_returnable_products = true;
                        message = 'Some product(s) of this order are unavailable in Point Of Sale, do you wish to return other products?'
                    }
                    else if (product.not_returnable) {
                        non_returnable_products = true;
                        message = 'This order contains some Non-Returnable products, do you wish to return other products?'
                    }
                    else if(line.qty - line.line_qty_returned > 0)
                        original_orderlines.push(line);
                });
                if(original_orderlines.length == 0){
                    self.gui.show_popup('my_message',{
                        'title': _t('Cannot Return This Order!!!'),
                        'body': _t("There are no returnable products left for this order. Maybe the products are Non-Returnable or unavailable in Point Of Sale!!"),
                    });
                }
                else if(non_returnable_products){
                    self.gui.show_popup('confirm',{
                        'title': _t('Warning !!!'),
                        'body': _t(message),
                        confirm: function(){
                            self.gui.show_popup('return_products_popup',{
                                'orderlines': original_orderlines,
                                'order':order,
                                'is_partial_return':true,
                            });
                        },
                    });
                }
                else{
                    self.gui.show_popup('return_products_popup',{
                        'orderlines': original_orderlines,
                        'order':order,
                        'is_partial_return':false,
                    });
                }
            }
            else
            {
                self.gui.show_popup('my_message',{
                    'title': _t('Warning!!!'),
                    'body': _t(message),
                });
            }
        }
    });
});

