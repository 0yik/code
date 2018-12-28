odoo.define('pos_modifier_kitchen_display.pos', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screenps = require('point_of_sale.screens');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var pos_restaurant_kitchen_widget = require('pos_restaurant_kitchen_widget');
    var Model = require('web.Model');
    
    var kitchen_screen = null
    for (var index in gui.Gui.prototype.screen_classes) {
        if(gui.Gui.prototype.screen_classes[index].name=='kitchen_screen'){
            kitchen_screen =gui.Gui.prototype.screen_classes[index].widget 
            gui.Gui.prototype.screen_classes.splice(index, 1);
        }
    }
    console.log('kitchen_screen   '+kitchen_screen)
    var KitchenScreenWidget = kitchen_screen.extend({
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
	            self.d1 = new Date();
	            console.log('this......',dir)
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
	        
	        stopTimer : function() {
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
	                console.log("dirrrrrrr", self.dir);
	                // calculate time difference between
	                // initial and current timestamp
	                if (self.dir === 'sw') {
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
        renderElement: function () {

            this._super();
            this.$('.subwindow-container-fix').html('')
            var self = this;
            var items = [];
            var orders_kanban = [];
            
            if (this.pos.config.screen_type == 'manager') {
                console.log('this is future for manager control all system');
                return;
            } else {
				if (this.pos.config.screen_type == 'kitchen') {
            		if ($('#cancel_refund_order').length > 0){
            			$('#cancel_refund_order').hide();
            		}
            	}
                var orders = this.pos.get('orders').models;
                var order = null;
                var categs = [];
                for (var i = 0; i < this.pos.config.categ_ids.length; i++) {
                    categs.push(this.pos.config.categ_ids[i]);
                }
                if (categs.length <= 0) {
                    console.log('kitchen screen: Categories have not set');
                    return;
                }
                if (orders.length <= 0) {
                    console.error('Order is empty');
                    return;
                }
                for (var i = 0; i < orders.length; i++) {
                    orders_kanban.push([])
                }
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    if(!orders_kanban[i]){
                        orders_kanban[i].push(order)
                    }
                    if (order.table) {
                        var table_id = order.table.id
                        var table = this.pos.tables_by_id[table_id]
                        if (!table) {
                            console.error('Order have not table, can not render')
                            continue;
                        }
                        for (var j = 0; j < order.orderlines.models.length; j++) {
                            var line = order.orderlines.models[j];
                            if (line.product.pos_categ_id[0] == undefined) {
                                console.log('category product line underfined');
                                continue;
                            }
                            if (line.state == 'Done') {
                                console.log('state is DONE, pass');
                                continue;
                            }
                            if (line.state == 'Need-to-confirm') {
                                console.log('Need-to-confirm, pass');
                                continue;
                            }
                            if (categs.indexOf(line.product.pos_categ_id[0]) == -1) {
                                console.log('Not the same category product and pos config category');
                                continue;
                            }
                            if (line.quantity_updated && line.quantity_updated < line.quantity) {
                                // alert('pushed lines')
                                items.push(line);
                                orders_kanban[i].push(line)
                            } else if (!line.quantity_updated) {
                                // alert('pushed lines')
                                items.push(line);
                                orders_kanban[i].push(line)
                            } else if (line.quantity_updated > line.quantity) {
                                console.log('quantity_updated > quantity of line')
                            }
                        }
                    }
                }
            }

            for (var item in orders_kanban) {
                if(orders_kanban[item].length>0){
                        var kitchen_line = $(qweb.render('KitchenKanban', {
                            widget: this,
                            order: orders_kanban[item][0],
                            lines:orders_kanban[item],
                        }));
                        
                        kitchen_line =  $(kitchen_line)
                        kitchen_line.appendTo(this.$('.subwindow-container-fix'))
                }
            }
            
            //order history
            var kitchen_order_history = $(qweb.render('KitchenOrders', {
                widget: this,
            }));
            kitchen_order_history =  $(kitchen_order_history)
            kitchen_order_history.appendTo(this.$('.subwindow-container-fix'))
            
            /*var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            
            ajax.jsonRpc("/history", 'call', {
	    	    }).then(function(res) {
	    	    	for(var i=0, len=Math.min(res.length,1000); i<len; i++){
	    	    		var order = res[i];
	    	    		var orderline_html = qweb.render('OrderHistroyLine',{widget: this, order:order});
	                    var orderline = document.createElement('tbody');
	                    orderline.innerHTML = orderline_html;
	                    orderline = orderline.childNodes[1];
	                    contents.appendChild(orderline);
	    	    	}
	    	    });*/
            
            // finished order History
            
            
            this.$('.done-all').click(function () {
            	self.stopTimer();
            	var ended_time = $(this).next('div').find('span#sw_h').text() + ':' + $(this).next('div').find('span#sw_m').text() + ':' + $(this).next('div').find('span#sw_s').text() + ':' + $(this).next('div').find('span#sw_ms').text();
                var line_id = $(this).data()['id'];
                var orders = self.pos.get('orders').models;
                var done_order = null
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    for (var j = 0; j < order.orderlines.models.length; j++) {
                        var line = order.orderlines.models[j];
                        if (line.id == line_id) {
                            done_order = line.order
                            break
                        }
                    }
                }
                for (var k = 0; k < done_order.orderlines.models.length; k++) {
                    var doneline = done_order.orderlines.models[k];
                    var order_line = JSON.stringify(doneline.export_as_JSON());
                    /*new Model("pos.order").call("manage_bom_stock", [[]],{'order_line':order_line}).then(function(results){
                        // sort activities by due date
                    	console.log("====");
                    });*/
                    var order_id = doneline.id;
                    new Model("order.history").call("update_orders", [], {'order_id':order_id, 'end_time':ended_time}).then(function(results){
                    	console.log("====", results);
                    });
                    doneline.set_state('Done');
                }
                
            });
            this.$('.strt').click(function(){
            	$(this).css('display', 'none');
            	self.startTimer('sw',$(this));
            	$(this).next('button').css("display","block");
            	$(this).next().next('.timer').css("display","block");
            	
            	var time_started = "00:00:00:00";
            	var line_id = $(this).data()['id'];
                var orders = self.pos.get('orders').models;
                var pending_order = null;
                var table_info = null;
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    for (var j = 0; j < order.orderlines.models.length; j++) {
                        var line = order.orderlines.models[j];
                        if (line.id == line_id) {
                        	pending_order = line.order;
                        	table_info = line.order.table.name;
                            break
                        }
                    }
                }
                //console.log("\n pendinnigngigingigign", pending_order.orderlines);
                for (var k = 0; k < pending_order.orderlines.models.length; k++) {
                    var pendingline = pending_order.orderlines.models[k];
                    console.log('\n pendinglinependingline', table_info);
                    var order_line = JSON.stringify(pendingline.export_as_JSON());
                    new Model("order.history").call("manage_order_history", [], {'order_line':order_line, 'start_time':time_started, 'table_info':table_info}).then(function(results){
                    	console.log("====", results);
                    });
                }
                
            });
            
            this.$('#tborder').click(function() {
            	$('#ordhist').removeClass('active');
            	$(this).addClass("active");
            	$('.ohistory').hide();
            	$('.client-card').show();
        	});
            this.$('#ordhist').click(function() {
            	$('#tborder').removeClass('active');
            	$(this).addClass("active");
            	$('.client-card').hide();
            	$('.ohistory').show();
                var contents = document.querySelector('.order-list-contents');
                contents.innerHTML = "";
                ajax.jsonRpc("/history", 'call', {
    	    	    }).then(function(res) {
    	    	    	for(var i=0, len=Math.min(res.length,1000); i<len; i++){
    	    	    		var order = res[i];
    	    	    		var orderline_html = qweb.render('OrderHistroyLine',{widget: this, order:order});
    	                    var orderline = document.createElement('tbody');
    	                    orderline.innerHTML = orderline_html;
    	                    orderline = orderline.childNodes[1];
    	                    contents.appendChild(orderline);
    	    	    	}
    	    	    });
        	});
            /*this.$('#sw_start').click(function() {
                self.startTimer('sw');
            });*/
            /*this.$('#sw_stop').on('click', function() {
                self.stopTimer();
            });*/
        },
    });
    gui.define_screen({
        'name': 'kitchen_screen',
        'widget': KitchenScreenWidget,
    });
    
    
    

});

