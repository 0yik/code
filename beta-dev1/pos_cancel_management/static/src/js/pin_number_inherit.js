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
            var pin = $('.popup-input').text().split(' ')[0].trim();
            var username = $('.username')
            var model = new Model('res.users');
            var dom = [];
            var error = 0;
            if (!$('.popup-input').html().trim().length){
                alert("Please enter the PIN first!");
            }
            else{
                var cashier = this.pos.check_pin_number(pin);
                if(cashier){
                    floorplan.pos.set_table(table);
                    self.pos.set_cashier(cashier);
                    username.text(cashier.name)
                    var order_lines = self.pos.get_order().get_orderlines();
                    var order_has_comfirmed = false;
                    order_lines.forEach(function(order){
                        if (order.state != "Cancelled"){
                            order_has_comfirmed = true;
                        }
                    });
                    if(order_has_comfirmed)return;
                    while (order_lines.length > 0){
                        self.pos.process_cancel_order(self.pos.get_order(), order_lines[0], 'delete');
                    }
                    return
                }else{
                    alert("You have entered a wrong PIN")
                }
                // model.call("search_read", [dom, ['pin_number', 'name']]).then(function (result) {
                //     for (var i = 0; i < result.length; i++){
                //         if (result[i].pin_number == pin && user == result[i].id){
                //             floorplan.pos.set_table(table);
                //             self.pos.set_cashier(result[i]);
                //             username.text(result[i].name);
                //             var order_lines = self.pos.get_order().get_orderlines();
                //             var order_has_comfirmed = false;
                //             order_lines.forEach(function(order){
                //                 if (order.state != "Cancelled"){
                //                     order_has_comfirmed = true;
                //                 }
                //             });
                //             if(order_has_comfirmed)return;
                //             while (order_lines.length > 0){
                //                 self.pos.process_cancel_order(self.pos.get_order(), order_lines[0], 'delete');
                //             }
                //             return
                //         }
                //         else{
                //                 error = 1
                //         }
                //     }
                //     if (error == 1){
                //             alert("You have entered a wrong PIN")
                //     }
                // });
            }
        },
    });

});