odoo.define('pos_show_popup_qty.pos_show_popup_qty', function (require) {
"use strict";

var devices = require('point_of_sale.devices');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var _t = core._t;

    screens.NumpadWidget.include({

        clickChangeMode: function(event) {
            this._super(event);
            var newMode = event.currentTarget.attributes['data-mode'].value;
            var user = this.pos.get_cashier();
            var order = this.pos.get_order();
            var line  = order.get_selected_orderline()
            var buton = $(_.str.sprintf('.mode-button[data-mode="%s"]', newMode), this.$el);
            // if (newMode === 'quantity' && line && line.mp_changeqty === undefined){
            //     line['mp_changeqty'] = false;
            // }else{
            //     this.gui.show_popup('error',_t('Please Select Order line first !!'));
            // }
            if (newMode === 'quantity' && line && line.state === 'Cancelled'){
                return alert('You can not update quantity on cancelled order.');
            }
            else if (newMode === 'quantity' && line ) {
                var self = this;
                this.gui.show_popup('number', {
                    'title':  _t('Qty ?'),
                    'cheap': true,
                    'value':   order.get_selected_orderline().quantity,
                    'confirm': function(value) {
                        value = Math.max(1,Number(value));
                        // self.pos.get_order().set_customer_count(value);
                        line.set_quantity(value);
                        // line['mp_changeqty'] = true;
                    },
                });
                buton.addClass('selected-mode');
                this._super(event);
            } else if ( newMode != 'quantity' ){
                this._super(event);
            } else  {
                this.gui.show_popup('error',_t('Please select order line first !'));
            }
            $(_.str.sprintf('.mode-button[data-mode="%s"]', newMode), this.$el).addClass('selected-mode');
        },
    });

    // screens.OrderWidget.include({
    //     set_value: function(val) {
    //         var order = this.pos.get_order();
    //         var line  = order.get_selected_orderline();
    //         if (line.quantity == 0){
    //             line['mp_changeqty'] = true
    //         }
    //         if (order.get_selected_orderline()) {
    //             var mode = this.numpad_state.get('mode');
    //             if( mode === 'quantity' && line['mp_changeqty'] && line.mp_changeqty === false){
    //                 order.get_selected_orderline().set_quantity(val);
    //             }else if( mode === 'discount'){
    //                 order.get_selected_orderline().set_discount(val);
    //             }else if( mode === 'price'){
    //                 order.get_selected_orderline().set_unit_price(val);
    //             }
    //         }
    //     },
    // });

});
