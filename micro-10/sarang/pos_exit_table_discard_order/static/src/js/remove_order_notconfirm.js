odoo.define('pos_exit_table_discard_order.remove_not_conform_order', function (require) {
"use strict";

//var PosBaseWidget = require('point_of_sale.BaseWidget');
var chrome = require('point_of_sale.chrome');
// var gui = require('point_of_sale.gui');
// var models = require('point_of_sale.models');
// var screens = require('point_of_sale.screens');
var core = require('web.core');
// var Model = require('web.DataModel');
var floor = require('pos_restaurant.floors')
var models = require('point_of_sale.models')
var QWeb = core.qweb;
var _t = core._t;
var gui = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');


var ConfirmPopupWidget = PopupWidget.extend({
    template: 'ConfirmPopupWidget',
});

chrome.OrderSelectorWidget.include({
    floor_button_click_handler: function(){
        
       
        
        
        var current_orders = this.pos.get_table_orders(this.pos.table)
        //console.log(current_orders);

        // var unpaid_orders=this.pos.db.get_unpaid_orders()
        // for (var i =0; i < this.pos.db.get_unpaid_orders().length; i++) 
        // {
            
        //     var line_length = unpaid_orders[i]['lines'].length
        //     if (unpaid_orders[i]['table'] == this.pos.table['name'])
        //     {
        //             console.log("prakash")
        //         for (var j=0; j<line_length; j++)
        //         {

        //             //console.log("+++++++-------------------",unpaid_orders[i]['lines'][j].length);
        //             for (var k=0; k< unpaid_orders[i]['lines'][j].length; k++)
        //             {

                        
        //                 if (unpaid_orders[i]['lines'][j][k]['state']=="Need-to-confirm")
        //                 {
        //                     console.log("========+++++++-------------------",unpaid_orders[i]['lines'][j][k]);
        //                     unpaid_orders[i].remove_orderline(unpaid_orders[i]['lines'][j][k])


        //                 }    
                        

        //             }


        //         }    
                    
        //     }
            


        //     //console.log("-------------------",unpaid_orders[i]['lines'].length);
        //     //console.log(unpaid_orders[i]['lines'].length);        
        // }
     
        var error = 0
        var order = this.pos.get_order();
        var lines = order.orderlines;
        for (var index=0; index < _.size(current_orders); index++) {
            var order = current_orders[index];
            var lines = order.orderlines;
            lines = lines.length > 0 ? lines.models: [];

            var self = this;
            var filtered_lines = _.filter(lines, function(l) {
                return l.state == 'Need-to-confirm' 
            });
            if (lines.length == filtered_lines.length){
                order.destroy({'reason':'abandon'});
            }
            for (var j=0; j < _.size(filtered_lines); j++)
            {   
                order.remove_orderline(filtered_lines[j]);
            }
            
            // for (var l in lines) {
            //     console.log('lllllllll', l, lines[l], lines[l].state);
            //     if (lines[l].state == 'Need-to-confirm') {
            //         order.remove_orderline(lines[l]);
            //     }
            // }
        }
        /*if (error == 1){
            this.gui.show_popup('confirm',{
            'title': _t('Destroy Current Order ?'),
            'body': _t('You will lose any data associated with the current order'),
            confirm: function(){
                self.pos.delete_current_order();
            },
            });
        }*/
        this.pos.set_table(null);
    },

});


});