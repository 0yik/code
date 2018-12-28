odoo.define('pos_delivery_timeframe_calendar.pos_delivery', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var delivery_order = require('pos_home_delivery.pos_delivery')
var _t = core._t;
var Model = require('web.Model');
var gui = require('point_of_sale.gui');
var ActionManager1 = require('web.ActionManager');
var monthsName = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];

var models = require('point_of_sale.models');

var _super_order_line = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    export_as_JSON: function () {
        var json = _super_order_line.export_as_JSON.apply(this, arguments);
        json.product_currency_symbol = this.pos.currency.symbol;
        json.product_name = this.product.name;
        json.product_uom_name = this.product.uom_id[1];
        return json;
    },
});

//Load timeframe data
models.load_models([
    {
        model: 'time.frame',
        fields: ['start', 'finish', 'price', 'qty',],
        loaded: function(self,result){
            if(result.length){
                //set time frame data in variable so that it can be fetched later using 
                //this.pos.get('timeframe');
                self.set('timeframe',result);
            }
        },
    },
    {
      model: 'pos.delivery.order',
        fields: ['delivery_date', 'order_no','state'],
        loaded: function(self,result){
        	self.pos_delivery_order = result;
            if(result.length){
                //set pos_delivery_order data in variable so that it can be fetched later using 
                //this.pos.get('pos_delivery_order');
                self.set('pos_delivery_order',result);
            }
        },  
    }],{'after': 'product.product'});

var home_delivery = require('TM_pos_receipt_extended.TM_pos_receipt_extended');
var HomeDeliveryWidget = screens.ActionButtonWidget.extend({
        template: 'HomeDeliveryNew1',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.orderlines.models;
            if(orderlines.length < 1){
                self.gui.show_popup('error',{
                        'title': _t('Empty Order !'),
                        'body': _t('Please select some products'),
                    });
                return false;
            }
            this.gui.show_popup('delivery_order',{
                'title': _t('Home Delivery Order'),
                'name' : order.get_div_name(),
                'email' : order.get_div_email(),
                'mobile' : order.get_div_mobile(),
                'address' : order.get_div_location(),
                'street' : order.get_div_street(),
                'city' : order.get_div_city(),
                'zip' : order.get_div_zip(),
                'delivery_date' : order.get_delivery_date() ,
                'person_id' : order.get_div_person(),
                'order_note' : order.get_div_note(),
            });
            models.load_models([
            {
                model: 'time.frame',
                fields: ['start', 'finish', 'price', 'qty',],
                loaded: function(self,result){
                    if(result.length){
                        //set time frame data in variable so that it can be fetched later using 
                        //this.pos.get('timeframe');
                        self.set('timeframe',result);
                    }
                },
            },
            {
              model: 'pos.delivery.order',
                fields: ['delivery_date', 'order_no'],
                loaded: function(self,result){
                	self.pos_delivery_order = result;
                    if(result.length){
                        //set pos_delivery_order data in variable so that it can be fetched later using 
                        //this.pos.get('pos_delivery_order');
                        self.set('pos_delivery_order',result);
                    }
                },  
            }],{'after': 'product.product'});

            var show_booked = function () {
                var selected_hours = $('#d-hh').html();
                var time_frames = self.pos.get('timeframe');
                var calendar_date = $('div.cursorily'); //get current calendar dates.
                var pos_delivery_order = self.pos.get('pos_delivery_order');
                var orderModel = new Model('pos.delivery.order');
                var domains = [];
                var fields = ['delivery_date', 'order_no','state'];
                orderModel.call('search_read',[domains,fields])
                	.then(function (delivery_orders) {
                		self.set('pos_delivery_order',delivery_orders);
                		pos_delivery_order = delivery_orders;
			                var selected_month = $('.dtp_modal-months').find('span').text().split(' ')[0];
			                var selected_month = monthsName.indexOf(selected_month);
			                var selected_year = parseInt($('.dtp_modal-months').find('span').text().split(' ')[1]);
			                for (var tf in time_frames){
			                    if (selected_hours <= time_frames[tf].finish && selected_hours >= time_frames[tf].start){
			                        for (var dt in calendar_date){
			                            if (dt == "length"){
			                                break;
			                            }
			                            var c_date = parseInt(calendar_date[dt].textContent)
			                            var dt_counter = 0;
			                            for (var p_order in pos_delivery_order){
			                            	var ordr_dt1 = new Date(new Date(pos_delivery_order[p_order].delivery_date).toString().slice(0,24) + ' UTC');
			                                var ordr_dt = ordr_dt1.getDate();
			                                var ordr_mnth = ordr_dt1.getMonth();
			                                var ordr_year = ordr_dt1.getFullYear();
			                                var ordr_hour = ordr_dt1.getHours();
			                                var state = pos_delivery_order[p_order].state;
			                                if (state != 'cancel' && c_date == ordr_dt && selected_month == ordr_mnth && selected_year == ordr_year){
			                                    if (ordr_hour <= time_frames[tf].finish && ordr_hour >= time_frames[tf].start){
			                                        dt_counter ++ ;
			                                    }	
			                                }
			                            }
			                            var qty = time_frames[tf].qty;
			                            if (dt_counter < qty){
			                                calendar_date[dt].classList.add('green-cls');
			                                calendar_date[dt].classList.remove('red-cls');
			                            }
			                            else{
			                                calendar_date[dt].classList.add('red-cls');
			                                calendar_date[dt].classList.remove('green-cls');
			                            }
			                        }
			
			                    }
			                }
                	});
            }
            
            $(document).off("click",'#datetimepicker1')
            .on("click","#datetimepicker1",function(){
                show_booked();
                $('#angle-down-hour').click(function(){
                    show_booked();
                });
                $('#angle-up-hour').click(function(){
                    show_booked();
                })
                var change_month_fun = function(){
                    $('i.ico-size-month').click(function(){
                        show_booked();
                        change_month_fun()
                    });
                }
                change_month_fun()
            });
        },
    });

screens.define_action_button({
        'name': 'home_delivery',
        'widget': HomeDeliveryWidget,
        'condition': function() {
            return true;
        },
    });

var DeliveryOrderWidget = PopupWidget.extend({
    template: 'DeliveryOrderWidget1',
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};
    },
    events: {
        'click .button.clear': 'click_clear',
        'click .button.cancel': 'click_cancel',
        'click .button.create': 'click_create',
    },
    show: function(options){
        this._super(options);
        this.renderElement();
        this.$('.d_name').focus();
    },
    get_orderline_data: function() {
        var order = this.pos.get_order();
        var orderlines = order.orderlines.models;
        var all_lines = [];
        for (var i = 0; i < orderlines.length; i++) {
            var line = orderlines[i]
            if (line && line.product && line.quantity !== undefined) {
                all_lines.push({
                    'product_id': line.product.id,
                    'qty': line.quantity,
                    'price': line.get_display_price(),
                    'note': line.get_note(),
                })
            }
        }
        return all_lines
    },
    click_create: function(){ 
        var self = this;
        var order = this.pos.get_order();
        var order_lines = self.get_orderline_data()
        if(order_lines.length > 0){
            var fields = {};
            this.$('.detail').each(function(idx, el){
                fields[el.name] = el.value || false;
            });
            order.set_delivery_data(fields);
            var d_date = new Date(fields.delivery_date);
            fields.delivery_date = d_date.toISOString();
            var empty = $(".body").find('input[required], select[required]').filter(function() {
                return this.value == '';
              });
            if (empty.length){
                self.gui.show_popup('error',{
                    'title': _t('Missing required'),
                    'body': _t('Some require details are missing OR you forget to give time in delivery date'),
                });
                return false;
            }
            var date = new Date();
            var order_date = date.toISOString();
            var order_data = {
                    'order_no' : order.name || order.uid || false,
                    'session_id': order.pos.pos_session.id || order.pos_session_id,
                    'order_date': order_date || false,
                    'cashier_id' : order.pos.user.id || false,
            }
            var result = {
                'form_data': fields,
                'order_data': order_data,
                'line_data' : order_lines
            }
            new Model('pos.delivery.order').call('delivery_order_from_ui',[result]).then(function(data){return data;},function(err,event){
                event.preventDefault();
                self.gui.show_popup('error',{
                    'title': _t('Delivery Order not Created'),
                    'body': _t('Please fill your details properly.'),
                });
                return false;
            });
            order.set_delivery_status(true);
            if (order.delivery){
            	if ($('#apply_charges').prop('checked')) {
                    var product_list = this.gui.screen_instances.products.product_list_widget.product_list
                    for (var prod in product_list){
                        if (product_list[prod].display_name == "Delivery Charges"){
                            product_list[prod].list_price == 50;
                            product_list[prod].lst_price == 50;
                            product_list[prod].price == 50;
                            //self.pos.get_order().add_product(product_list[prod]);
                            order_lines = self.pos.get_order().orderlines.models
                            for (var line in order_lines){
                                if (order_lines[line].product.display_name == "Delivery Charges"){
                                    //get timeframe objects
                                    var time_frames = this.pos.get('timeframe')
                                    var dt = new Date(); //get current date
                                    var current_time = dt.getHours() //get current hour
                                    var ordr_dt1 = new Date(d_date.toString().slice(0,24));
	                                var ordr_dt = ordr_dt1.getDate();
	                                var ordr_mnth = ordr_dt1.getMonth();
	                                var ordr_year = ordr_dt1.getFullYear();
	                                var ordr_hour = ordr_dt1.getHours();
                                    for (var tf in time_frames){
                                        if (ordr_hour <= time_frames[tf].finish && ordr_hour >= time_frames[tf].start){
                                            //set the price according to hours.
                                            order_lines[line].set_unit_price(time_frames[tf].price);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                else{
                    var order_lines = this.gui.pos.get_order().orderlines.models
                    for (var line in order_lines){
                        if (order_lines[line].product.display_name == "Delivery Charges"){
                            order_lines[line].set_quantity(0);
                        }
                    }
                }
                alert('Delivery order successfully created');
            }
            this.gui.close_popup();
        }
        
    },
    click_clear: function(){
        this.$('.detail').val('');
        this.$('.d_name').focus();
    },
    click_cancel: function(){
        this.gui.close_popup();
        if (this.options.cancel) {
            this.options.cancel.call(this);
         }
    },
});
gui.define_popup({name:'delivery_order', widget: DeliveryOrderWidget});

});

