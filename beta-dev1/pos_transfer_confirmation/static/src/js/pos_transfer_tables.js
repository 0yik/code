// confirm(
odoo.define('pos_transfer_confirmation.pos_transfer_tables', function (require) {
"use strict";

var models = require('point_of_sale.models');
var floors = require('pos_restaurant.floors');


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        set_table: function(table) {
            if (!this.order_to_transfer_to_different_table){
                this.old_table = table;
                var res = _super_posmodel.set_table.apply(this, arguments);
                return res;
            }
            if (table && this.order_to_transfer_to_different_table){ 
                var msg;
                var count_table = this.get_count_need_print(table)
                if(count_table.active_print > 0 || count_table.unactive_print > 0){
                    alert(table.name +" table is reserved");

                    this.order_to_transfer_to_different_table.table = this.old_table;
                    this.order_to_transfer_to_different_table.save_to_db();
                    this.order_to_transfer_to_different_table = null;
                    this.table = this.old_table;
                    
                    this.set_table(this.table);
                    var orders = this.get_order_list();
                    if (orders.length)
                    {
                        this.set_order(orders[0]); // and go to the first one ...
                    } else {
                        this.add_new_order();  // or create a new order with the current table
                    }
                }
                else{
                    msg = confirm("You are going to transfer the guest from "+this.old_table.name +" on "+this.old_table.floor_id[1] +" to "+table.name +" on "+ table.floor_id[1] +", confirm?")
                    if (!msg)
                    {
                        this.order_to_transfer_to_different_table.table = this.old_table;
                        this.order_to_transfer_to_different_table.save_to_db();
                        this.order_to_transfer_to_different_table = null;
                        this.table = this.old_table;
                        this.set_table(this.table);
                        
                        var orders = this.get_order_list();
                        if (orders.length)
                        {
                            this.set_order(orders[0]); // and go to the first one ...
                        } else {
                            this.add_new_order();  // or create a new order with the current table
                        }
                    }
                    else{
                        var res = _super_posmodel.set_table.apply(this, arguments);
                        return res;
                    }
                }
            }
            else{
                var res = _super_posmodel.set_table.apply(this, arguments);
                return res;
            }
        },
    });

});