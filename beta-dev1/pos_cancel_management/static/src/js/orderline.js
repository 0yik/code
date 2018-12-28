odoo.define('pos_cancel_management.orderline', function (require) {
"use strict";

    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var QWeb = core.qweb;
    var _t = core._t;
    var _super_order = models.Order.prototype;
    var floors = require('pos_restaurant.floors');
    floors.TableWidget.include({
        get_pin_number: function(floorplan, table){
            console.log('debug one');
            var self = this;
            var user = this.pos.user.id;
            var table = this.table;
            var pin = $('.popup-input').text();
            var username = $('.username')
            var model = new Model('res.users');
            var dom = []
            var error = 0
            if (!$.trim( $('.popup-input').html()).length){
                alert("Please enter the PIN first!");
            }
            else{
                model.call("search_read", [dom, ['pin_number', 'name']]).then(function (result) {
                    for (var i = 0; i < result.length; i++){
                        if (result[i].pin_number == pin && user == result[i].id ){
                                floorplan.pos.set_table(table);
                                self.pos.set_cashier(result[i]);
                                username.text(result[i].name);
                                var order_lines = self.pos.get_order().get_orderlines();
                                var order_has_comfirmed = false;
                                order_lines.forEach(function(order){
                                    if (order.state != "Cancelled"){
                                        order_has_comfirmed = true;
                                    }
                                });
                                if(order_has_comfirmed)return;
                                while (order_lines.length > 0){
                                        // order.set_order_invisible(true);
                                    self.pos.process_cancel_order(self.pos.get_order(), order_lines[0], 'delete');
                                }

                                // order_lines.forEach(function(order){
                                //     if (order.state == "Cancelled"){
                                //         order.set_order_invisible(true);
                                //         self.pos.process_cancel_order(order_lines, order, 'delete');
                                //     }
                                // });
                                // $('.orderlines .orderline').each(function () {
                                //     if($(this).find('.Cancelled').length > 0){
                                //         $(this).css('display','none');
                                //     }
                                // });
                                return
                        }
                        else{
                                error = 1
                        }
                    }
                    if (error == 1){
                            alert("You have entered a wrong PIN")
                    }
                    //self.renderElement();
                    /*if (pin == result[0].pin_number){
                            floorplan.pos.set_table(table);
                    }
                    else{
                            alert("You have entered a wrong PIN")
                    }*/
                });
            }
        },
    });
    var _super_orderline = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		set_order_invisible: function(order_invisible){
            this.order_invisible = order_invisible;
        },
        get_order_invisible: function(order_invisible){
            return this.order_invisible;
        },
	});

});
