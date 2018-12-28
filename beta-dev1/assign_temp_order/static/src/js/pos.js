odoo.define('assign_temp_order.pos', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var QWeb = core.qweb;
    var bus = require('pos_bus_bus');
    
    var OrderLine = models.Orderline.prototype;

    var Order = models.Order.prototype;
    var Bus = bus.bus.prototype
    var PopupWidget = require('point_of_sale.popups');
    var chrome = require('point_of_sale.chrome');
    var session = require('web.session');
	var tableGuest = require('pos_restaurant.floors');

    var PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        sync_order_adding: function (vals) {
            var orders = this.get('orders');
            if(!this.get_order_by_uid(vals.uid)){
                PosModel.sync_order_adding.apply(this, arguments);
            }
            
        },

    });
    bus.bus = bus.bus.extend({
        push_message_to_other_sessions: function (value) {
            let self = this;
            if(self.pos.config.screen_type=='e_menu'){
                console.log(">>>>>>> push_message_to_other_sessions >>>>> in if emenu_orde");
                var orders = this.pos.get('orders').models;
                let orders_store = []
                for (var i = 0; i < orders.length; i++) {
                    orders_store.push(orders[i].export_as_JSON())
                }
                var need_sync = true
                if(typeof(value.order) === 'object' && value.order.temp_order){
                    need_sync = false
                }
                if(need_sync){
                    let message = {
                        user_send_id: this.pos.user.id,
                        value: value,
                    };
                    var sending = function () {
                        return session.rpc("/longpolling/pos/bus", {
                            message: message,
                            orders_store: orders_store
                        });
                    };
                    sending().fail(function (error, e) {
                        console.error(error);
                        if (error.message == "XmlHttpRequestError ") {
                            self.pos.db.save_data_false(message);
                            console.log(' Sync False ')
                        }
                    }).done(function () {
                        self.repush_to_another_sessions();
                        console.log(' Sync DONE ')
                    });
                }
                
            }
            else{
                Bus.push_message_to_other_sessions.call(this, value);
            }
            

        },
        get_message_from_other_sessions: function (messages) {
            console.log(">>>>>> get_message_from_other_sessions ", messages.length, messages)
            for (var i = 0; i < messages.length; i++) {
                let message = messages[i];
                if(message[1]['value']){
                    this.pos.syncing_sessions(message[1]['value']);
                }
            }
        },
        
        
    });

    var floor_screen = null
    models.load_models({
        model: 'restaurant.floor',
        fields: ['name','background_color','table_ids','sequence'],
        domain: function(self){
					if(self.gui.pos.config.screen_type=='e_menu' || self.gui.pos.config.screen_type=='kitchen'){
						return [];
					} else {
						return [['pos_config_ids','in',self.config.id]]; 
					}
				},
        loaded: function(self,floors){
            if(self.config.screen_type=="e_menu" || self.config.screen_type=="kitchen"){
                self.floors = [];
                self.floors_for_temp = floors
                self.floors_by_id = {};
                for (var i = 0; i < floors.length; i++) {
                    floors[i].tables = [];
                    self.floors_by_id[floors[i].id] = floors[i];
                }
                self.config.iface_floorplan = 0
                self.floors_for_temp = self.floors_for_temp.sort(function(a,b){ return a.sequence - b.sequence; });
            }
            else{
                self.floors = floors;
                self.floors_by_id = {};
                for (var i = 0; i < floors.length; i++) {
                    floors[i].tables = [];
                    self.floors_by_id[floors[i].id] = floors[i];
                }
                self.floors = self.floors.sort(function(a,b){ return a.sequence - b.sequence; });
                self.config.iface_floorplan = !!self.floors.length;
            }
        },
    });
    models.load_models({
        model: 'restaurant.table',
        fields: ['name','width','height','position_h','position_v','shape','floor_id','color','seats'],
        loaded: function(self,tables){
            self.tables_by_id = {};
            for (var i = 0; i < tables.length; i++) {
                self.tables_by_id[tables[i].id] = tables[i];
                var floor = self.floors_by_id[tables[i].floor_id[0]];
                if (floor) {
                    floor.tables.push(tables[i]);
                    tables[i].floor = floor;
                }
            }
        },
    });

// At POS Startup, after the floors are loaded, load the tables, and associate
// them with their floor.

    var ChooseTablePopupWidget = PopupWidget.extend({
        template: 'ChooseTable',
        show: function(options){
        options = options || {};
        this._super(options);

        this.renderElement();
        this.chrome.widget.keyboard.connect(this.$('input'));
        this.$('input,textarea').focus();
    },
    click_confirm: function(){
        var value = this.$('select').val();
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,value);
        }
    },
    });

    gui.define_popup({name:'chooseTable', widget:ChooseTablePopupWidget});

    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            if(!options.json){
                this.temp_order = false
                this.set_temp_customer_name(null);
            }           
            Order.initialize.apply(this, arguments); 
            if(!options.json && this.pos.config.screen_type == 'e_menu'){
                this.temp_order = true;
                this.emenu_order = true;
                this.dine_is_assign_order = false;
                this.set_temp_customer_name(null);
            }
           
        },
        init_from_JSON: function(json) {
            Order.init_from_JSON.call(this, json);
            this.temp_order = json.temp_order;
            this.emenu_order = json.emenu_order;
            this.dine_is_assign_order = json.dine_is_assign_order;
            this.temp_customer_name = json.temp_customer_name;
        },
        export_as_JSON: function() {
            var ret=Order.export_as_JSON.call(this);
            ret.temp_order = this.temp_order;
            ret.emenu_order = this.emenu_order;
            ret.dine_is_assign_order = this.dine_is_assign_order;
            ret.temp_customer_name = this.temp_customer_name;
            return ret;
        },
        set_temp_customer_name(temp_customer_name){
            this.temp_customer_name = temp_customer_name;
            if($('.temp_customer_name').length){

                $('.temp_customer_name').val(temp_customer_name);
            }
        },
        set_temp_order: function(value){
            this.temp_order = value;
            this.category = "dive_in";
            this.popup_option = 'Dine In'
            if (!value) {
                this.pos.pos_bus.push_message_to_other_sessions({
                    data: this.export_as_JSON(),
                    action: 'new_order',
                    bus_id: this.pos.config.bus_id[0],
                    order: this.export_as_JSON(),
                });
                // this.destroy({'reason':'send to kitchen order.'});
            }
        }
    });

    screens.ProductScreenWidget.include({
        show: function(reset){
            this._super();
            var order = this.pos.get_order();
            if(order && order.pos && order.pos.popup_option == "Dine In"){
                $('.autoassign-order').removeClass('oe_hidden');
            }
            else{
                $('.autoassign-order').addClass('oe_hidden');   
            }

             if(this.pos.config.screen_type == 'e_menu'){
                if(!order || !order.temp_order){
                    $('.sendTempOrder').removeClass('oe_hidden');
                    $('button.pay').removeClass('oe_hidden');
                    $('.autoassign-order').removeClass('oe_hidden');
                    $('.paymentplan_btn').removeClass('oe_hidden');
                    $('.set-customer').removeClass('oe_hidden');
                }else{
                    $('.sendTempOrder').removeClass('oe_hidden');
                    $('button.pay').addClass('oe_hidden');
                    $('.autoassign-order').addClass('oe_hidden');
                    $('.paymentplan_btn').addClass('oe_hidden');
                    $('.set-customer').addClass('oe_hidden');

                    if($(".pos .number-char").length){
                        for (var i = $(".pos .number-char").length - 1; i >= 0; i--) {
                            $(".pos .number-char")[i].setAttribute("style", "width: 67px !important;");
                        }
                    }

                    if($(".pos .mode-button").length){
                        for (var i = $(".pos .mode-button").length - 1; i >= 0; i--) {
                            $(".pos .mode-button")[i].setAttribute("style", "width: 67px !important;");
                        }
                    }
                    
                    if( $(".pos .numpad-minus").length){
                        $(".pos .numpad-minus")[0].setAttribute("style", "width: 67px !important;");
                    }
                    if( $(".pos .numpad-backspace").length){
                        $(".pos .numpad-backspace")[0].setAttribute("style", "width: 67px !important;");
                    }
                    if( $(".pos .centerpane .numpad").length){
                        $(".pos .centerpane .numpad")[0].setAttribute("style", "width: 90% !important;");
                    }

                } 
            }
                 
        },
     
    });
    

    var TempOrdersScreenWidget = screens.ScreenWidget.extend({
        template: 'TempOrdersScreenWidget',

        get_customer: function(customer_id){
            var self = this;
            if(self.gui)
                return self.gui.get_current_screen_param('customer_id');
            else
                return undefined;
        },
        render_list: function(order, input_txt) {
            var self = this;
            var customer_id = this.get_customer();
            var new_order_data = [];
            if(customer_id != undefined){
                for(var i=0; i<order.length; i++){
                    if(order[i].get_client() == customer_id)
                        new_order_data = new_order_data.concat(order[i]);
                }
                order = new_order_data;
            }
            if (input_txt != undefined && input_txt != '') {
                var new_order_data = [];
                var search_text = input_txt.toLowerCase()
                for (var i = 0; i < order.length; i++) {
                    if (((order[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order[i].get_client_name().toLowerCase()).indexOf(search_text) != -1)) {
                        new_order_data = new_order_data.concat(order[i]);
                    }
                }
                order = new_order_data;
            }
            var contents = this.$el[0].querySelector('.temp-order-list-contents');
            contents.innerHTML = "";
            var temp_orders = order;
            for (var i = 0, len = Math.min(temp_orders.length, 1000); i < len; i++) {
                var temp_order = temp_orders[i];
                var orderline_html = QWeb.render('tempOrderLine', {
                    widget: this,
                    order: temp_orders[i],
                    index:i,
                    order_date:temp_orders[i].creation_date,
                });
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            }
            var tables = []
            if(self.pos.floors_for_temp){

                for (var i = self.pos.floors_for_temp.length - 1; i >= 0; i--) {
                    var floor = self.pos.floors_for_temp[i]
                    for (var j = floor.tables.length - 1; j >= 0; j--) {
                        var table_name = floor.tables[j]['name']+' ('+floor['name']+')'
                        tables.push([floor.tables[j]['id'],  table_name])
                    }
                }
            }
            self.$('.temp-order-list-contents').delegate('.temp-order-line', 'click', function(event) {
                var order = temp_orders[parseInt($(this).data('index'))]
                self.line_select(event, order, tables );
            });
        },
        line_select: function(event, order, tables) {
            var self = this;
            // self.gui.show_popup('chooseTable', {
            //     'title': 'Choose Table For Order',
            //     'tables': tables,
            //     'confirm': function(val) {
            //         order.table = self.pos.tables_by_id[val];
            //         order.set_temp_order(false);
            //         self.show();
            //     },
            // });

        },
        show: function() {
            var self = this;
            this._super();
            var orders = self.pos.get('orders').models;
            var temp_orders = []
            for (var i = orders.length - 1; i >= 0; i--) {
                if(orders[i].temp_order){
                    temp_orders.push(orders[i])
                }
            }
            if(this.pos.category == 'dive_in'){
                for (var i = orders.length - 1; i >= 0; i--) {
                    // if(orders[i].temp_order){
                        temp_orders.push(orders[i])
                    // }
                } 
            }
            this.render_list(temp_orders, undefined);
            this.$('.order_search').keyup(function() {
                self.render_list(temp_orders, this.value);
            });
            this.$('.back').on('click',function() {
                self.gui.show_screen('products');
                if(self.pos.get_order() && !self.pos.get_order().temp_order){
                    $('button.pay').removeClass('oe_hidden');
                }
            });
        },
        close: function() {
            this._super();
            this.$('.temp-order-list-contents').undelegate();
        },
    });
    gui.define_screen({name: 'temp_order',widget:TempOrdersScreenWidget});

    var AssignOrders = screens.ActionButtonWidget.extend({
        template: 'AssignOrders',
        button_click: function () {
            this.pos.gui.show_screen('temp_order',{});
        },
    });
    screens.define_action_button({
        'name': 'AssignOrders',
        'widget': AssignOrders,
        'condition': function () {
            return true;
            // return this.pos.config.screen_type == 'e_menu';
        }
    });
    var sendTempOrder = screens.ActionButtonWidget.extend({
        template: 'sendTempOrder',
        button_click: function () {
            var order = this.pos.get_order();
            if (order){
                order.temp_customer_name = $('.temp_customer_name').val();
                console.log("order.temp_customer_name ", order.temp_customer_name, order);
                console.log("order.temp_customer_name ", order.orderlines.length, order.orderlines);
                if(!order.temp_customer_name){
                    alert("Please input cutomer name");
                    
                }
                else if(order.orderlines.length == 0){
                    alert("Please add products for order ");
                }
                else{

                    order.set_temp_order(false);
                    alert('Order send to waiter screen.');
                }
            }
            else{
                alert("Order not find to send");
            }
        },
    });
    screens.define_action_button({
        'name': 'sendTempOrder',
        'widget': sendTempOrder,
        'condition': function () {
            return true;
            // return this.pos.config.screen_type == 'e_menu';
        }
    });


	screens.define_action_button({
		'name': 'guests',
		'widget': tableGuest.TableGuestsButton,
		'condition': function(){
				if(this.pos.config.screen_type=='e_menu'){
		    		return true;
				} else {
					this.pos.config.iface_floorplan;
				}
		},
	});

	// auto assign order
    var AutoAssignOrders = screens.ActionButtonWidget.extend({
        template: 'AutoAssignOrders',
        button_click: function () {
			var tables_obj = [];
			for (var l=0; l < this.pos.floors_for_temp.length; l++) {
				tables_obj.push(this.pos.floors_for_temp[l]['tables']);
			}
			tables_obj = tables_obj[0].concat(tables_obj[1])
			var guests = this.pos.get_order().get_customer_count(); // guest qty < = seats;
			var tables = []
            for (var i = this.pos.floors_for_temp.length - 1; i >= 0; i--) {
                var floor = this.pos.floors_for_temp[i]
                for (var j = floor.tables.length - 1; j >= 0; j--) {
                    var table_name = floor.tables[j]['name']+' ('+floor['name']+')';
					var seats = floor.tables[j]['seats'];
                    tables.push([floor.tables[j]['id'],  table_name, seats])
                }
            }
			var occu_tables = [];
			_.each(this.pos.get('orders').models, function(v, k){
				if (v.table){
					occu_tables.push(v.table.id);
				}
			});
			for (var k=0; k < occu_tables.length; k++){
				for (var j=0; j < tables.length; j++) {
					if(tables[j][0] == occu_tables[k]){
						tables.pop(tables[j]);
					}
				}
			}
			tables = tables.reverse();
			var assign_tbl = null;
			for (var n=0; n < tables.length; n++) {
				if(tables[n][2] >= guests){
					assign_tbl = tables[n];
					break;
				}
			}
			var sel_tbl = null;
			for (var tbl=0; tbl < tables_obj.length; tbl++){
				if (tables_obj[tbl]['id'] == assign_tbl[0]){
					sel_tbl = tables_obj[tbl];
					break;
				}
			}
			this.pos.get_order().table = sel_tbl;
            this.pos.pos_bus.push_message_to_other_sessions({
                action: 'order_transfer_new_table',
                data: {
                    uid: this.pos.get_order().uid,
                    table_id: sel_tbl.id,
                    floor_id: sel_tbl.floor_id[0],
                },
                order: this.pos.get_order().export_as_JSON(),
                bus_id: this.pos.config.bus_id[0],
            });
            this.pos.get_order().set_temp_order(false);
        },
    });
    screens.define_action_button({
        'name': 'AutoAssignOrders',
        'widget': AutoAssignOrders,
        'condition': function () {
            return (this.pos.config.screen_type == 'e_menu' || this.pos.config.is_auto_assign_order == true);
            // return this.pos.config.is_auto_assign_order == true;
        }
    });

    //self.pos.config.screen_type=='e_menu'
    screens.ProductScreenWidget.include({

		show: function(){
			this._super();
			if(this.pos.config.screen_type=='e_menu'){
                $('div.control-button:contains("Rewards")').remove();
                $('button.go-back-staff-meal').remove();
                $('button.order-submit').remove();
                $('.control-button:contains("All Orders")').remove();
                $('.CreateSalesOrderbutton').remove();
                //$('.service-charge-button').remove();
            }
		}
	});

    var TempCustomerName = screens.ActionButtonWidget.extend({
        template: 'TempCustomerName',
        button_click: function () {
           
        },
    });
    screens.define_action_button({
        'name': 'TempCustomerName',
        'widget': TempCustomerName,
        'condition': function () {
            return this.pos.config.screen_type == 'e_menu' ;
        }
    });

    chrome.OrderSelectorWidget.include({
        order_click_handler: function(event,$el) {
            var order = this.get_order_by_uid($el.data('uid'));
            if (order) {
                order.set_temp_customer_name('');
                $('.temp_customer_name').val('');
                this.pos.set_order(order);
            }
        },

    });
    return {
        TempOrdersScreenWidget:TempOrdersScreenWidget,
        AutoAssignOrders:AutoAssignOrders,
        sendTempOrder:sendTempOrder,
        TempCustomerName:TempCustomerName,
    }

});
