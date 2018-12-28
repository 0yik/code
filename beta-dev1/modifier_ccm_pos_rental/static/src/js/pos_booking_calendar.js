odoo.define('modifier_ccm_pos_rental.pos_booking_calendar', function(require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var time = require('web.time');
var booking_cal = require('pos_rental.pos_rental');

var QWeb = core.qweb;
var _t = core._t;

	booking_cal.PosBookingCalendar.include({
	    validate_dates: function(product, laundry_buffer) {
	        var self = this;
	        var selectedOrder = this.pos.get('selectedOrder');
	        if (selectedOrder.wk_selected_dates) {
	            if (selectedOrder.wk_selected_dates.length>0) {
	                var selected = selectedOrder.wk_selected_dates;
	                var selected_data = new Array();
	                var offset = 0;
	                selected.forEach(function(dat) {
	                    offset = dat.getTimezoneOffset();
	                    var tzDifference = -dat.getTimezoneOffset();
	                    dat = new Date(dat.getTime() + tzDifference*60  * 1000);
	                    selected_data.push(time.datetime_to_str(dat));
	                });
	                selected_data.sort();
	                var min = selected_data[0];
	                var max = selected_data[selected_data.length - 1];
	                var min1 = new Date(min);
	                var max1 = new Date(max);
	                var dd = max1.getDate();
	                var mm = max1.getMonth()+1;
	                var yyyy = max1.getFullYear();
	                var return_date = mm+'/'+dd+'/'+yyyy;
	
	                var diff = (((((max1-min1)/1000)/60)/60)/24) +1;
                    self.add_product_to_booking_order(product, laundry_buffer).then(function (val) {
                        if (val) {
                            var price = self._calculate_rent_price(diff, product.rent_price);
                            selectedOrder.booked_lines[product.id] = {'start': min, 'end': max,'product_qty':1, 'laundry_buffer':laundry_buffer}
                            selectedOrder.add_product(product, {quantity:1, 'check': 'check', price:price, merge:false});
                            var line_with_book = selectedOrder.get_selected_orderline();
                            line_with_book.collect_date = min;
                            line_with_book.return_date = max;
                            line_with_book.is_ordered = true;
                            line_with_book.is_booked = true;
                            selectedOrder.return_date = return_date;
                            selectedOrder.selected_orderline.advance_deposit = product.advance_deposit;
                            if (self.pos.config.advance_product_id) {
                                var prod = {'product': self.pos.db.get_product_by_id(self.pos.config.advance_product_id[0])};
                                selectedOrder.add_product(prod, {quantity:1, 'check': 'check', price:0, merge:false});
                            }
                            var line = selectedOrder.selected_orderline;
                            line.set_quantity(1);
                        }
                    });
	            } else {
	               alert('No dates Selected!!!'); 
	            }
	        } else {
	            alert('No dates Selected!!!');
	        }
	    }
	});

});