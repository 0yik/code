odoo.define('pos_cashier_station.cashier', function(require) {
    'use strict'

    var models = require('point_of_sale.models');
    
    models.load_fields("pos.config",['session_type']);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // changes the current table.
        set_table: function(table) {
            if (!table) { // no table ? go back to the floor plan, see ScreenSelector
                this.set_order(null);
            } else if (this.order_to_transfer_to_different_table) {
                this.order_to_transfer_to_different_table.table = table;
                this.order_to_transfer_to_different_table.save_to_db();
                this.order_to_transfer_to_different_table = null;

                // set this table
                this.set_table(table);

            } else {
                this.table = table;
                var orders = this.get_order_list();
                if (orders.length) {
                    if (this.config.session_type == 'cashier'){
                        
                        var has_valid_product_lot = _.every(orders[0].orderlines.models, function(line){
                            return line.has_valid_product_lot();
                        });
                        if(!has_valid_product_lot){
                            this.gui.show_popup('confirm',{
                                'title': _t('Empty Serial/Lot Number'),
                                'body':  _t('One or more product(s) required serial/lot number.'),
                                confirm: function(){
                                    this.set_order(orders[0])
                                    this.gui.show_screen('payment');
                                },
                            });
                        }else{
                            this.set_order(orders[0])
                            this.gui.show_screen('payment');
                        }
                    }
                    else {
                        this.set_order(orders[0]); // and go to the first one ...
                        }
                } else {
                    this.add_new_order();  // or create a new order with the current table
                }
            }
        },
    });
});