odoo.define('complex_kds.models', function (require) {

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    models.load_models({
        model: 'restaurant.floor',
        fields: ['name','background_color','table_ids','sequence'],
        // domain: function(self){ return [[]]; },
        loaded: function(self,floors){
            self.floors_all = floors;
            self.floors_all_by_id = {};
            for (var i = 0; i < floors.length; i++) {
                floors[i].tables = [];
                self.floors_all_by_id[floors[i].id] = floors[i];
            }
            self.floors_all = self.floors_all.sort(function(a,b){ return a.sequence - b.sequence; });
        },
    });

    models.load_models({
        model: 'restaurant.table',
        fields: ['name','width','height','position_h','position_v','shape','floor_id','color','seats'],
        loaded: function(self,tables){
            self.tables_all_by_id = {};
            for (var i = 0; i < tables.length; i++) {
                self.tables_all_by_id[tables[i].id] = tables[i];
                var floor = self.floors_all_by_id[tables[i].floor_id[0]];
                if (floor) {
                    floor.tables.push(tables[i]);
                    tables[i].floor = floor;
                }
            }
        },
    });
    var OrderLine = models.Orderline.prototype;
    models.load_fields('product.product', ['normal_time_cook']);
    models.load_models({
        model: 'category.mapping.line',
        fields: ['categ_ids', 'next_pos_config_id','ip_address','config_id',],
        domain: function(self){ return [['config_id','=',self.config.id]]; },
        loaded: function(self, category_mappings){
            self.category_mappings = category_mappings
            self.next_screen_by_categ = {}
            console.log('HELLL',category_mappings)
            for (var i = 0; i < category_mappings.length; i++) {
                for (var j = 0; j < category_mappings[i].categ_ids.length; j++) {
                    self.next_screen_by_categ[category_mappings[i].categ_ids[j]] = category_mappings[i].next_pos_config_id;
                }
            }
        },
    });
    models.load_models({
        model: 'category.mapping.line',
        fields: ['categ_ids', 'next_pos_config_id','ip_address','config_id',],
        domain: function(self){ return [['config_id2','=',self.config.id]]; },
        loaded: function(self, summary_mappings){
            self.summary_mappings = summary_mappings
            self.summary_by_categ = {}
            for (var i = 0; i < summary_mappings.length; i++) {
                for (var j = 0; j < summary_mappings[i].categ_ids.length; j++) {
                    self.summary_by_categ[summary_mappings[i].categ_ids[j]] = summary_mappings[i].next_pos_config_id;
                }
            }
        },
    });
    var PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        syncing_sessions: function(message) {
            if(message){
                var self = this
                PosModel.syncing_sessions.apply(this, arguments);
                if (message['action'] == 'sync_next_screen') {
                    this.sync_next_screen(message['data'])
                }
                if (message['action'] == 'transfer_out') {
                    this.show_message_from_other_branchs(message);
                }
                if (message['action'] == 'sync_set_note') {
                    this.sync_set_note(message['data'])
                }
                if (message['action'] == 'sync_new_pack_line') {
                    this.sync_new_pack_line(message['data'])
                }
                var action = message['action'];
                if (action == 'new_order' && message['branch_id']) {
                    console.log('ggggggggggg')
                    var order = this.get_order_by_uid(message['data']['uid']);
                    console.log('ffffffffff  category     ',order.category)
                    console.log('pop up option    ', order.popup_option)
                    if(order.popup_option=='Delivery'){
                        self.pos_bus.push_message_to_other_sessions({
                            data: order.export_as_JSON(),
                            action: 'new_order',
                            bus_id: self.config.bus_id[0],
                            order: order.export_as_JSON(),
                        });
                        var orderlines = order.orderlines.models;
                        for (var i = 0; i < orderlines.length; i++) {
                            var line = orderlines[i]
                            if (orderlines[i].state && orderlines[i].state == 'Need-to-confirm') {
                                if(line.product.pos_categ_id){
                                    if(line.product.pos_categ_id[0] in self.next_screen_by_categ){
                                        line.next_screen = self.next_screen_by_categ[line.product.pos_categ_id[0]]
                                    }
                                    if(line.product.pos_categ_id[0] in self.summary_by_categ){
                                        line.summary_screen = self.summary_by_categ[line.product.pos_categ_id[0]]
                                    }
                                    this.pos_bus.push_message_to_other_sessions({
                                        action: 'sync_next_screen',
                                        data: {
                                            uid: line.uid,
                                            next_screen: line.next_screen,
                                            summary_screen: line.summary_screen,
                                            popup_option: 'Transfer Out',
                                            reward: line.reward
                                        },
                                        order: line.export_as_JSON(),
                                        bus_id: this.config.bus_id[0],
                                    });
                                }
                                orderlines[i].syncing = false
                                orderlines[i].set_state('Confirmed');
                                this.pos_bus.push_message_to_other_sessions({
                                    action: 'set_state',
                                    data: {
                                        uid: line.uid,
                                        state: 'Confirmed',
                                    },
                                    order: line.export_as_JSON(),
                                    bus_id: this.config.bus_id[0],
                                });
                            }
                        }
                        order.popup_option = 'Transfer Out'

                    }
                    // this.sync_order_adding(message['data']);
                }
                if (message['action'] == 'set_state') {
                    var vals = message['data'];
                    var line = this.get_line_by_uid(vals['uid']);
                    if (line && vals['state']=='Confirmed') {
                        line.timer_starttime = Date.now();
                        this.set_order_confirmation_time(line.order)
                    };
                }
                if (this.config.screen_type == 'summary') {
                    this.trigger('update:summaryscreen');
                }
                if (this.config.screen_type == 'kitchen') {
                    this.trigger('update:kitchenscreen');
                }

            }
        },
        get_pack_line_by_uid: function (uid) {
            var lines = [];
            var orders = this.get('orders').models;
            for (var i = 0; i < orders.length; i++) {
                var order = orders[i];
                for (var j = 0; j < order.pack_product_lines.models.length; j++) {
                    lines.push(order.pack_product_lines.models[j]);
                }
            }
            for (line_index in lines) {
                if (lines[line_index].uid == uid) {
                    return lines[line_index];
                }
            }
        },
        sync_new_line: function (vals) {
            var order = this.get_order_by_uid(vals['order_uid'])
            if (order) {
                order.syncing = true;
                var product = this.db.get_product_by_id(vals['product_id']);
                if (!product) {
                    this.load_new_product_by_id(vals['product_id']);
                    product = this.db.get_product_by_id(vals['product_id']);
                }
                if (product) {
                    order.add_product(product, {
                        price: vals['price_unit'],
                        quantity: vals['qty'],
                        merge:false,
                    });
                    order.selected_orderline.syncing = true;
                    order.selected_orderline.uid = vals['uid'];
                    order.selected_orderline.session_info = vals['session_info'];
                    order.selected_orderline.trigger('change', order.selected_orderline);
                    order.selected_orderline.syncing = false;
                };
                order.syncing = false;
            }
        },
        sync_new_pack_line: function (vals) {
            console.log('   sync_new_pack_linesync_new_pack_line    ',vals)
            var order = this.get_order_by_uid(vals['order_uid'])
            if (order) {
                order.syncing = true;
                var product = this.db.get_product_by_id(vals['product_id']);
                if (!product) {
                    this.load_new_product_by_id(vals['product_id']);
                    product = this.db.get_product_by_id(vals['product_id']);
                }
                if (product) {
                    var line = new models.Orderline({}, {pos: this, order: order, product: product, json:vals});
                    line.set_quantity(vals['qty']);
                    order.pack_product_lines.add(line);
                    line.syncing = true;
                    line.uid = vals['uid'];
                    line.session_info = vals['session_info'];
                    // line.trigger('change', order.selected_orderline);
                    line.syncing = false;
                };
                order.syncing = false;
            }
        },
        sync_set_note: function(vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.note = vals['note']
            };
            this.trigger('update:kitchenscreen');
            // this.trigger('update:summaryscreen');
        },
        set_order_confirmation_time: function(order){
            if(!order.confirmation_time){
                var date = false
                for (var i = order.orderlines.models.length - 1; i >= 0; i--) {
                    if(!date){
                        date = order.orderlines.models[i].timer_starttime
                        continue
                    }
                    date = Math.min(date, order.orderlines.models[i].creation_date)
                }
                order.confirmation_time = date
            }
        },
        delete_current_order: function(){
            var order = this.get_order();
            console.log('Session  ',this)
            console.log('Order  ',order)
            if(order && order.popup_option=='Delivery' && !order.permantly_delete){
                console.log('uuuuuuuu  this.pos_session.branch_id[0]   ',this.pos_session.branch_id[0])
                console.log('tttttttttt   order.receiver_branch_id  ',order.receiver_branch_id)
                if(this.pos_session.branch_id[0]==order.receiver_branch_id){
                    console.log('HELOOOOOOOOOOOOO  INSIDE BRANCH ')
                    order.remove_from_summary = true
                    order.saveChanges()
                }else{
                    // order.popup_option = 'Transfer Out'
                    this.pos_bus.push_message_to_other_branches({
                        data: order.export_as_JSON(),
                        action: 'new_order',
                        branch_id: order.receiver_branch_id,
                        order: order.export_as_JSON(),
                    });
                    order.remove_from_summary = false
                }
            }
            else if(order){
                order.remove_from_summary = false
            }
            PosModel.delete_current_order.apply(this, arguments);
        },
        sync_order_removing: function (vals) {
            var order = this.get_order_by_uid(vals.uid);
            if (order && !order.remove_from_summary){
                PosModel.sync_order_removing.apply(this, arguments);
            }
        },
        sync_order_transfer_new_table: function (vals) {
            var order = this.get_order_by_uid(vals.uid);
            var current_screen = this.gui.get_current_screen();
            if (order != undefined) {
                if (this.floors_all_by_id[vals.floor_id] && this.tables_all_by_id[vals.table_id]) {
                    var table = this.tables_all_by_id[vals.table_id];
                    var floor = this.floors_all_by_id[vals.floor_id];
                    if (table && floor) {
                        order.table = table;
                        order.table_id = table.id;
                        order.floor = floor;
                        order.floor_id = floor.id;
                        order.trigger('change', order);
                        if (current_screen) {
                            this.gui.show_screen(current_screen);
                        }
                    }
                    if (!table || !floor) {
                        order.table = null;
                        order.trigger('change', order);
                    }
                }
            }
        },
        sync_next_screen: function(vals) {
            var line = this.get_line_by_uid(vals['uid']);
            if(!line){
                line = this.get_pack_line_by_uid(vals['uid'])
            }
            if (line) {
                line.syncing = true;
                line.next_screen = vals['next_screen'];
                line.summary_screen = vals['summary_screen'];
                this.play_sound();
                line.syncing = false;
                console.log('   vals   ',vals)
                if('total_seconds' in vals){
                    line.total_seconds = vals['total_seconds']
                }
                if('timer_starttime' in vals){
                    line.timer_starttime = vals['timer_starttime']
                }
                if('creation_date' in vals){
                    line.creation_date = vals['creation_date']
                }
                if('order_confirm_date' in vals){
                    line.order.confirmation_time = vals['order_confirm_date']
                }
                if('popup_option' in vals){
                    line.popup_option = vals['popup_option']
                }
                if('reward' in vals){
                    line.reward = vals['reward']
                }
                if('is_pack' in vals){
                    line.is_pack = vals['is_pack']
                }
                
            };
            this.trigger('update:kitchenscreen');
            this.trigger('update:summaryscreen');
        },
        sync_order_adding: function (vals) {
            if(this.config.screen_type=='kitchen' || this.config.screen_type=='summary' || this.config.screen_type=='takeaway'){
                var orders = this.get('orders');
                if (vals.floor_id && vals.table_id) {  // if installed pos_restaurant module of Odoo
                    if (this.floors_all_by_id[vals.floor_id] && this.tables_all_by_id[vals.table_id]) {
                        var table = this.tables_all_by_id[vals.table_id];
                        var floor = this.floors_all_by_id[vals.floor_id];
                        var orders = this.get('orders');
                        if (table && floor) {
                            var order = new models.Order({}, {pos: this, json: vals});
                            this.order_sequence += 1;
                            order.syncing = true;
                            orders.add(order);
                            order.trigger('change', order);
                            order.syncing = false;
                        }
                    }
                } else { // not installed pos_restaurant Odoo
                    var order = new models.Order({}, {pos: this, json: vals});
                    this.order_sequence += 1;
                    order.syncing = true;
                    orders.add(order);
                    order.trigger('change', order);
                    order.syncing = false;
                    if (orders.length == 1) {
                        this.set('selectedOrder', order);
                    }
                }
                // this.trigger('update:summaryscreen');
            }else{
                PosModel.sync_order_adding.apply(this, arguments);
            }


        },

    });
    var Paymentline = models.Paymentline.prototype;

    models.Paymentline = models.Paymentline.extend({
        initialize: function(attributes, options) {
            try{
                   Paymentline.initialize.apply(this, arguments);
                }
            catch(e){
                }
        },
        init_from_JSON: function(json){
            try{
                   Paymentline.init_from_JSON.apply(this, arguments);
                }
            catch(e){
                this.amount = json.amount;
                }
        },
        export_as_JSON: function() {
            var loaded = {}
            try{
                  loaded = Paymentline.export_as_JSON.apply(this, arguments);
                }
            catch(e){
                return loaded
                }
                return loaded
        },
    });


// [finally {
//     // Code that is always executed regardless of 
//     // an exception occurring
// }]

    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            this.creation_date  = Date.now();
            this.timer_starttime  = Date.now();
            // this.next_screen = false
            OrderLine.initialize.apply(this, arguments);
        },
        set_note: function(note){
            var self = this
            this.note = note;
            this.trigger('change',this);
            this.order.pos.pos_bus.push_message_to_other_sessions({
                action: 'sync_set_note',
                data: {
                    uid: self.uid,
                    note: self.note
                },
                order: self.export_as_JSON(),
                bus_id: self.order.pos.config.bus_id[0],
            });
        },
        init_from_JSON: function(json) {
            if(json.creation_date){
            this.creation_date = json.creation_date;}
            if(json.timer_starttime){
            this.timer_starttime = json.timer_starttime;}
            this.next_screen = json.next_screen
            this.summary_screen = json.summary_screen
            this.total_seconds = json.total_seconds
            this.cancel_manager = json.cancel_manager
            this.is_pack = json.is_pack
            this.main_pack_line = json.main_pack_line
            OrderLine.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function() {
            var loaded = OrderLine.export_as_JSON.apply(this, arguments);
            loaded.creation_date = this.creation_date;
            loaded.timer_starttime = this.timer_starttime;
            loaded.next_screen = this.next_screen
            loaded.summary_screen = this.summary_screen
            loaded.total_seconds = this.total_seconds
            loaded.cancel_manager = this.cancel_manager
            loaded.is_pack = this.is_pack
            loaded.main_pack_line = this.main_pack_line
            return loaded;
        },
        can_be_merged_with: function(orderline){
            if(orderline.reward==true){
                return false
            }
            var res = OrderLine.can_be_merged_with.apply(this, arguments);
            return res
        },
        set_quantity: function(quantity){
            var self = this;
            quantity = quantity==0 ? 'remove': quantity;
            var args = arguments;
            if(quantity === 'remove' && self.pos.config.screen_type=='waiter' && this.state=='Confirmed'){
                var res = confirm("You want to cancel this order, confirm?");
                if (res){
                    self.pos.gui.show_popup('number', {
                        'title':  _t('Enter PIN Number'),
                        'cheap': true,
                        'value': '',
                        'confirm': function(value) {
                            var pin = $('.popup-input').text();
                            if(!pin.trim()){
                                alert('Please Enter PIN First!')
                                return false
                            }
                            else{
                                var model = new Model('res.users');
                                model.call("compare_pin_number_get_manager", [pin]).then(function (result) {
                                    if (result){
                                        // OrderLine.set_quantity.apply(self, args);
                                        var order = self.order
                                        // order.cancelled_lines.push(self)
                                        console.log('Cancelled Line  Befoe   '+order.cancelled_lines.length)
                                        self.cancel_manager = result
                                        order.add_cancelled_orderline(self)
                                        console.log('Cancelled Line  After   '+order.cancelled_lines.length)
                                        self.set_state('Cancel')
                                        console.log('Cancelled Line  After  Delete '+order.cancelled_lines.length)
                                        return
                                    }
                                    else{
                                        alert("You have entered a wrong PIN")
                                    }
                                });
                            }
                        },
                        'cancel': function(){
                             return false
                        }
                    });
                }
            }else{
                    OrderLine.set_quantity.apply(self, args);
            }
        },
        formatTimer : function(a) {
                if (a < 10) {
                    a = '0' + a;
                }                              
                return a;
        },    
        startTimer : function(dir,date,from_summary) {
            var self = this;
            var a;
            // save type
            self.dir = dir;
            self.date = date;
            // get current date
            self.d1 = new Date(self.date)
            self.from_summary = from_summary
            switch(self.state) {
                case 'pause' :
                    // resume timer
                    // get current timestamp (for calculations) and
                    // substract time difference between pause and now
                    self.t1 = self.d1.getTime() - self.td;                            
                break;
                    
                default :
                    // get current timestamp (for calculations)
                    self.t1 = self.d1.getTime();
                break;
                    
            }                                   
            
            // reset state
            self.state = 'alive';   
            //$('#' + self.dir + '_status').html('Running');
            
            // start loop
            self.loopTimer();
        },
        
        stopTimer : function(dir) {
            var self = this;
            // change button value
            $('#' + self.dir + '_start').val('Restart');
            
            // set state
            self.state = 'stop';
            $('#' + self.dir + '_status').html('Stopped');
            
        },
        
        resetTimer : function() {
            var self = this;
            // reset display
            $('#' + self.dir + '_ms,#' + self.dir + '_s,#' + self.dir + '_m,#' + self.dir + '_h').html('00');            
            // change button value
            $('#' + self.dir + '_start').val('Start');                    
            
            // set state
            self.state = 'reset';  
            $('#' + self.dir + '_status').html('Reset & Idle again');
            
        },
        
        endTimer : function(callback) {
            var self = this;
            // change button value
            $('#' + self.dir + '_start').val('Restart');
            
            // set state
            self.state = 'end';
            
            // invoke callback
            if (typeof callback === 'function') {
                callback();
            }    
            
        },    
        
        loopTimer : function() {
            var self = this;
            var td;
            var d2,t2;
            
            var ms = 0;
            var s  = 0;
            var m  = 0;
            var h  = 0;
            if (self.state === 'alive') {
                // get current date and convert it into 
                // timestamp for calculations
                d2 = new Date();
                t2 = d2.getTime();   
                // calculate time difference between
                // initial and current timestamp
                if (self.dir.indexOf("sw") >= 0) {
                    td = t2 - self.t1;
                // reversed if countdown
                } else {
                    td = self.t1 - t2;
                    if (td <= 0) {
                        // if time difference is 0 end countdown
                        self.endTimer(function(){
                            self.resetTimer();
                            //$('#' + self.dir + '_status').html('Ended & Reset');
                        });
                    }    
                }    
                // calculate milliseconds
                ms = td%1000;
                if (ms < 1) {
                    ms = 0;
                } else {    
                    // calculate seconds
                    s = (td-ms)/1000;
                    if (s < 1) {
                        s = 0;
                    } else {
                        // calculate minutes   
                        var m = (s-(s%60))/60;
                        if (m < 1) {
                            m = 0;
                        } else {
                            // calculate hours
                            var h = (m-(m%60))/60;
                            if (h < 1) {
                                h = 0;
                            }                             
                        }    
                    }
                }
                // substract elapsed minutes & hours

                ms = Math.round(ms/100);
                s  = s-(m*60);
                m  = m-(h*60);                                
                // update display
                $('.' + self.dir + '_ms').html(self.formatTimer(ms));
                $('.' + self.dir + '_s').html(self.formatTimer(s));
                $('.' + self.dir + '_m').html(self.formatTimer(m));
                $('.' + self.dir + '_h').html(self.formatTimer(h));
                
                if(self.from_summary){
                    var normaltime = self.product.normal_time_cook
                    var total_seconds = (td/1000)/self.get_quantity()
                    if(normaltime < total_seconds){
                        if(((normaltime)+(normaltime*10/100))>=total_seconds){
                            background_color = 'yellow'
                            $('.' + self.dir + '_ms').parent().parent().css({'background-color':'yellow'})
                        }else{
                            background_color = 'red'
                            font_color='white'
                            $('.' + self.dir + '_ms').parent().parent().css({'background-color':'red', 'color': 'white'})
                        }
                    }
                }
                // loop
                self.t = setTimeout(function() {
                            self.loopTimer(); 
                        }, 1);
            
            } else {
                // kill loop
                clearTimeout(self.t);
                return true;
            
            }  
            
        },
    });
    var Backbone = window.Backbone;
    var OrderlineCollection = Backbone.Collection.extend({
    model: models.Orderline,
    });

    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            this.confirmation_time  = false;
            this.remove_from_summary = false;
            this.cancelled_lines  = new OrderlineCollection();
            this.pack_product_lines  = new OrderlineCollection();
            Order.initialize.apply(this, arguments); 
            if(!options.json || !('popup_option' in options.json)){                
                this.popup_option = this.pos.popup_option
                if(this.pos.popup_option=='Staff Meal' || this.pos.popup_option=='Take Away' || this.pos.popup_option=='Delivery' ){
                    this.remove_from_summary = true
                }
            }

        },
        init_from_JSON: function(json) {
            Order.init_from_JSON.apply(this,arguments);
            if(json.confirmation_time){
            this.confirmation_time = json.confirmation_time;}
            if(this.pos.config.screen_type=='kitchen' || this.pos.config.screen_type=='summary' || this.pos.config.screen_type=='takeaway'){
                this.table = this.pos.tables_all_by_id[json.table_id];
                this.floor = this.table ? this.pos.floors_all_by_id[json.floor_id] : undefined;
                this.customer_count = json.customer_count || 1;
            }
            this.popup_option = json.popup_option
            this.remove_from_summary = json.remove_from_summary
            var orderlines = json.cancelled_lines ? json.cancelled_lines :  new OrderlineCollection();
            for (var i = 0; i < orderlines.length; i++) {
                var orderline = orderlines[i][2];
                this.add_cancelled_orderline(new models.Orderline({}, {pos: this.pos, order: this, json: orderline}));
            }  
            var orderlines = json.pack_product_lines ? json.pack_product_lines :  new OrderlineCollection();
            for (var i = 0; i < orderlines.length; i++) {
                var orderline = orderlines[i][2];
                this.add_pack_product_line(new models.Orderline({}, {pos: this.pos, order: this, json: orderline}));
            }   

        },
        export_as_JSON: function() {
            var ret=Order.export_as_JSON.call(this);
            ret.confirmation_time = this.confirmation_time;
            ret.popup_option = this.popup_option;
            ret.remove_from_summary = this.remove_from_summary
            var orderLines;
            orderLines = [];
            this.cancelled_lines.each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            ret.cancelled_lines = orderLines
            var pack_orderLines = [];
            this.pack_product_lines.each(_.bind( function(item) {
                return pack_orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            ret.pack_product_lines = pack_orderLines
            return ret;
        },
        add_cancelled_orderline: function(line){
            this.assert_editable();
            if(line.order){
                line.order.remove_orderline(line);
            }
            line.order = this;
            this.cancelled_lines.add(line);
            // this.select_orderline(this.get_last_orderline());
        },
        add_pack_product_line: function(line){
            this.assert_editable();
            var self=this
            // if(line.order){
            //     line.order.remove_orderline(line);
            // }
            line.order = this;            
            if(this.pos.config.screen_type=='waiter' && !line.next_screen){
                 if(line.product.pos_categ_id[0] in self.pos.next_screen_by_categ){
                    line.next_screen = self.pos.next_screen_by_categ[line.product.pos_categ_id[0]]
                }
                if(line.product.pos_categ_id[0] in self.pos.summary_by_categ){
                    line.summary_screen = self.pos.summary_by_categ[line.product.pos_categ_id[0]]
                }
                console.log('line.next_screen   ',line.summary_screen,self.pos.summary_by_categ)

                // this.pos.pos_bus.push_message_to_other_sessions({
                //     action: 'sync_next_screen',
                //     data: {
                //         uid: line.uid,
                //         next_screen: line.next_screen,
                //         summary_screen: line.summary_screen,
                //         popup_option: line.popup_option ? line.popup_option : line.order.popup_option,
                //         reward: line.reward,
                //     },
                //     order: line.order.export_as_JSON(),
                //     bus_id: line.pos.config.bus_id[0],
                // });                
            }
            this.pack_product_lines.add(line);
            this.selected_packline = line
            // this.select_orderline(this.get_last_orderline());
        },
        add_orderline: function(line){
            var self=this;
            Order.add_orderline.apply(this, arguments);
            if(this.pos.config.screen_type=='waiter' && this.selected_orderline && !this.selected_orderline.next_screen){
                var line = this.selected_orderline
                var pack_products = line.getPackProduct(line.get_product().id,line.get_display_price(),line.get_quantity_str())
                if(line.product.pos_categ_id[0] in self.pos.next_screen_by_categ && !pack_products){
                    line.next_screen = self.pos.next_screen_by_categ[line.product.pos_categ_id[0]]
                }
                if(line.product.pos_categ_id[0] in self.pos.summary_by_categ && !pack_products){
                    line.summary_screen = self.pos.summary_by_categ[line.product.pos_categ_id[0]]
                }
                console.log('line.next_screen   ',line.summary_screen,self.pos.summary_by_categ)
                console.log('pack_products   ',pack_products)
                if(pack_products){
                    for (var i = pack_products.pack_product_list.length - 1; i >= 0; i--) {
                        var product = self.pos.db.product_by_id[pack_products.pack_product_list[i].product.id]
                        var l = new models.Orderline({}, {pos: self.pos, order: self, product: product});
                        self.add_pack_product_line(l)
                        this.selected_packline.set_quantity(pack_products.pack_product_list[i].qty)
                        this.selected_packline.main_pack_line = line.uid
                        self.pos.pos_bus.push_message_to_other_sessions({
                            data: this.selected_packline.export_as_JSON(),
                            action: 'sync_new_pack_line',
                            bus_id: self.pos.config.bus_id[0],
                            order: self.export_as_JSON(),
                        });
                    }
                }
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'sync_next_screen',
                    data: {
                        uid: line.uid,
                        next_screen: !pack_products ? line.next_screen : false,
                        summary_screen: line.summary_screen,
                        popup_option: line.popup_option ? line.popup_option : line.order.popup_option,
                        reward: line.reward,
                        is_pack: pack_products ? true :false,
                    },
                    order: line.export_as_JSON(),
                    bus_id: line.pos.config.bus_id[0],
                });

                // this.pos.pos_bus.push_message_to_other_sessions({
                //     action: 'sync_next_screen',
                //     data: {
                //         uid: line.uid,
                //         next_screen: line.next_screen,
                //         summary_screen: line.summary_screen,
                //         popup_option: line.popup_option ? line.popup_option : line.order.popup_option,
                //         reward: line.reward,
                //     },
                //     order: line.export_as_JSON(),
                //     bus_id: line.pos.config.bus_id[0],
                // });                
            }
            // this.assert_editable();
            // if(line.order){
            //     line.order.remove_orderline(line);
            // }
            // line.order = this;
            // this.orderlines.add(line);
            // this.select_orderline(this.get_last_orderline());
        },
        add_product: function(product, options){
            var self = this
            console.log('options.merge    ',options)
            if(options && 'extras' in options && 'reward_id' in options.extras){
                options.merge = false
            }
            Order.add_product.call(this, product, options);
            var line = this.get_selected_orderline()
            line.reward = false
            var pack_products = line.getPackProduct(line.get_product().id,line.get_display_price(),line.get_quantity_str())
            console.log('resilt   ',pack_products)
            if(options && 'extras' in options && 'reward_id' in options.extras){
                line.reward = true
            }
            if((!options && line.product.pos_categ_id) || line.reward){
                console.log('ttt    ',line.product.pos_categ_id[0], self.pos.next_screen_by_categ, pack_products)
                if(line.product.pos_categ_id[0] in self.pos.next_screen_by_categ && !pack_products){
                    line.next_screen = self.pos.next_screen_by_categ[line.product.pos_categ_id[0]]
                }
                if(line.product.pos_categ_id[0] in self.pos.summary_by_categ && !pack_products){
                    line.summary_screen = self.pos.summary_by_categ[line.product.pos_categ_id[0]]
                }
                // var pack_lines = []
                if(pack_products){
                    for (var i = pack_products.pack_product_list.length - 1; i >= 0; i--) {
                        // console.log('ppppppp      ',self.pos.db.product_by_id)
                        var product = self.pos.db.product_by_id[pack_products.pack_product_list[i].product.id]
                        var l = new models.Orderline({}, {pos: self.pos, order: self, product: product});
                        self.add_pack_product_line(l)
                        this.selected_packline.set_quantity(pack_products.pack_product_list[i].qty)
                        this.selected_packline.main_pack_line = line.uid
                        self.pos.pos_bus.push_message_to_other_sessions({
                            data: this.selected_packline.export_as_JSON(),
                            action: 'sync_new_pack_line',
                            bus_id: self.pos.config.bus_id[0],
                            order: self.export_as_JSON(),
                        });
                        // pack_lines.push(this.selected_packline)
                    }
                }
                console.log('>>>>>>>>>>>>>>>   ffffffff   line.next_screen    ',line.next_screen,!pack_products ? line.next_screen : false)
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'sync_next_screen',
                    data: {
                        uid: line.uid,
                        next_screen: !pack_products ? line.next_screen : false,
                        summary_screen: line.summary_screen,
                        popup_option: line.popup_option ? line.popup_option : line.order.popup_option,
                        reward: line.reward,
                        is_pack: pack_products ? true :false,
                    },
                    order: line.export_as_JSON(),
                    bus_id: line.pos.config.bus_id[0],
                });
            }
            else if(options && options.next_screen){
                line.next_screen = options.next_screen
            }
        },
        formatTimer : function(a) {
            if (a < 10) {
                a = '0' + a;
            }                              
            return a;
        },    
        startTimer : function(dir,space) {
            var self = this;
            var a;
            // save type
            self.dir = dir;
            self.space = space;
            // get current date
            self.d1 = new Date(this.confirmation_time)
            switch(self.state) {
                case 'pause' :
                    // resume timer
                    // get current timestamp (for calculations) and
                    // substract time difference between pause and now
                    self.t1 = self.d1.getTime() - self.td;                            
                break;
                    
                default :
                    // get current timestamp (for calculations)
                    self.t1 = self.d1.getTime();
                break;
                    
            }                                   
            
            // reset state
            self.state = 'alive';   
            //$('#' + self.dir + '_status').html('Running');
            
            // start loop
            self.loopTimer();
            
        },
        
        stopTimer : function(dir) {
            var self = this;
            // change button value
            $('#' + self.dir + '_start').val('Restart');                    
            
            // set state
            self.state = 'stop';
            $('#' + self.dir + '_status').html('Stopped');
            
        },
        
        resetTimer : function() {
            var self = this;
            // reset display
            $('#' + self.dir + '_ms,#' + self.dir + '_s,#' + self.dir + '_m,#' + self.dir + '_h').html('00');                 
            
            // change button value
            $('#' + self.dir + '_start').val('Start');                    
            
            // set state
            self.state = 'reset';  
            $('#' + self.dir + '_status').html('Reset & Idle again');
            
        },
        
        endTimer : function(callback) {
            var self = this;
            // change button value
            $('#' + self.dir + '_start').val('Restart');
            
            // set state
            self.state = 'end';
            
            // invoke callback
            if (typeof callback === 'function') {
                callback();
            }    
            
        },    
        
        loopTimer : function() {
            var self = this;
            var td;
            var d2,t2;
            
            var ms = 0;
            var s  = 0;
            var m  = 0;
            var h  = 0;
            if (self.state === 'alive') {
                // get current date and convert it into 
                // timestamp for calculations
                d2 = new Date();
                t2 = d2.getTime();   
                // calculate time difference between
                // initial and current timestamp
                if (self.dir.indexOf("sw") >= 0) {
                    td = t2 - self.t1;
                // reversed if countdown
                } else {
                    td = self.t1 - t2;
                    if (td <= 0) {
                        // if time difference is 0 end countdown
                        self.endTimer(function(){
                            self.resetTimer();
                            //$('#' + self.dir + '_status').html('Ended & Reset');
                        });
                    }    
                }    
                
                // calculate milliseconds
                ms = td%1000;
                if (ms < 1) {
                    ms = 0;
                } else {    
                    // calculate seconds
                    s = (td-ms)/1000;
                    if (s < 1) {
                        s = 0;
                    } else {
                        // calculate minutes   
                        var m = (s-(s%60))/60;
                        if (m < 1) {
                            m = 0;
                        } else {
                            // calculate hours
                            var h = (m-(m%60))/60;
                            if (h < 1) {
                                h = 0;
                            }                             
                        }    
                    }
                }
              
                // substract elapsed minutes & hours
                ms = Math.round(ms/100);
                s  = s-(m*60);
                m  = m-(h*60);                                
                // update display
                $('.' + self.dir + '_ms').html(self.formatTimer(ms));
                $('.' + self.dir + '_s').html(self.formatTimer(s));
                $('.' + self.dir + '_m').html(self.formatTimer(m));
                $('.' + self.dir + '_h').html(self.formatTimer(h));
                
                // loop
                self.t = setTimeout(function() {
                            self.loopTimer(); 
                        }, 1);
            
            } else {
                // kill loop
                clearTimeout(self.t);
                return true;
            
            }  
            
        },
    });
});