odoo.define('pos_bus_screen', function (require) {

    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        rerender_orderline: function (order_line) {
            try {
                this._super(order_line);
            } catch (e) {

            }
        },
        remove_orderline: function(order_line){
            try {
                this._super(order_line);
            } catch  (e) {

            }
        },
        update_summary: function(){
            try {
                this._super()
            } catch (e) {

            }
        },
    });
})