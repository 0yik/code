odoo.define('complex_kds.kitchen_screen', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var ajax = require('web.ajax');
    var pos_restaurant_kitchen_widget = require('pos_restaurant_kitchen_widget');
    var pos_restaurant_kitchen_screen = require('pos_restaurant_kitchen_screen');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        // Check if the order is paid, then sends it to the backend,
        // and complete the sale process
        validate_order: function(force_validation) {
            var order = this.pos.get_order();
            if(order.popup_option=='Staff Meal' || order.popup_option=='Take Away'){
                order.saveChanges();
            }
            this._super(force_validation);
        },
    });

    var kitchen_screen = null
    for (var index in gui.Gui.prototype.screen_classes) {
        if(gui.Gui.prototype.screen_classes[index].name=='kitchen_screen'){
            kitchen_screen =gui.Gui.prototype.screen_classes[index].widget 
            gui.Gui.prototype.screen_classes.splice(index, 1);
        }
    }
    var KitchenScreenWidget = kitchen_screen.extend({
        renderElement: function () {
            var self = this
            this._super();
            this.$('.subwindow-container-fix-kitchen').html('')
            var self = this;
            var items = [];
            var orders_kanban = [];
            if (this.pos.config.screen_type == 'manager') {
                console.log('this is future for manager control all system');
                return;
            } else if(this.pos.config.screen_type == 'kitchen'){
                $('.username').hide();
                $('.order-selector').hide();
                $('.pos-screenname').text(self.pos.config.name)
                var orders = this.pos.get('orders').models;
                // console.log('Orders     Length  ',orders.orderlines.models.length, orders)
                var order = null;
                var categs = [];
                if (orders.length <= 0) {
                    console.error('Order is empty');
                    return;
                }
                for (var i = 0; i < orders.length; i++) {
                    orders_kanban.push([[]])
                }
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    if(!orders_kanban[i]){
                        orders_kanban[i].push(order)
                    }
                    // if (order.popup_option=='Staff Meal') {
                        
                        if(order.table){
                            var table_id = order.table.id
                            var table = this.pos.tables_all_by_id[table_id]
                        }
                        var last_line = null
                        console.log('Hello   ',order.pack_product_lines)
                        console.log('OrderLine Length  ',order.orderlines.models.length)
                        for (var j = order.orderlines.models.length -1; j >=0 ; j--) {
                            var line = order.orderlines.models[j];
                            console.log('line...   ....  ',line.product.display_name,line.next_screen)
                            if (line.product.pos_categ_id[0] == undefined && !line.is_pack ) {
                                console.log('category product line underfined');
                                continue;
                            }
                            if (line.state == 'Done') {
                                console.log('state is DONE, pass');
                                continue;
                            }
                            if (line.state == 'Need-to-confirm') {
                                console.log('State : '+line.state +"  So it is passed");
                                continue;
                            }
                            if((line.next_screen && line.next_screen[0] == self.pos.config.id) && !line.is_pack){
                                console.log('line.next_screen    ',line.next_screen)
                                var ord_len = orders_kanban[i].length -1
                                orders_kanban[i][ord_len].push(line);
                            }
                            if(line.is_pack){
                                for (var k = order.pack_product_lines.length - 1; k >= 0; k--) {
                                    var l= order.pack_product_lines.models[k]
                                    console.log('uuuuuuuuubbbbbbbb    ',l.main_pack_line,l.next_screen)
                                    if(l.next_screen && l.next_screen[0] == self.pos.config.id && l.main_pack_line==line.uid){
                                        console.log('Yeahh added    ',l.reward_id)
                                        l.parent_pack_name = line.product.display_name
                                        var ord_len = orders_kanban[i].length -1
                                        orders_kanban[i][ord_len].push(l);
                                    }
                                }
                            }
                        }
                }
            }
            this.orders_kanban = orders_kanban
            console.log(orders_kanban)

            for (var item in orders_kanban) {
                if(orders_kanban[item].length>0){
                    for (var i = orders_kanban[item].length - 1; i >= 0; i--) {
                        for (var j = orders_kanban[item][i].length - 1; j>= 0; j--) {
                            console.log('>>>     ',i,j)
                            var line = orders_kanban[item][i][j];
                            var popup_option = line.popup_option ? line.popup_option : line.order.popup_option
                            var popup_option = popup_option=='dive_in_take_away' ? 'Take Away' : popup_option;
                            var kitchen_line = $(qweb.render('KitchenKanban', {
                            widget: this,
                            category: line.product.pos_categ_id[1],
                            id: line.id,
                            qty: line.quantity,
                            name: line.product.display_name,
                            note: line.note,
                            reward: line.reward,
                            uid: line.uid,
                            popup_option:popup_option,
                            color: popup_option in self.pos.order_category_by_name ? self.pos.order_category_by_name[popup_option].card_color : '0',
                            floor:line.order.table ? line.order.table.floor.name : '',
                            table:line.order.table ? line.order.table.name : '',
                            customer:line.order.get_client(),
                            parent_pack_name:line.parent_pack_name,
                            }));
                            $(kitchen_line).appendTo(this.$('.subwindow-container-fix-kitchen'))
                            line.startTimer('sw_'+line.uid,line.timer_starttime);
                            new Model("order.history").call("manage_order_line_history", [], {
                                'order_line':JSON.stringify(line.export_as_JSON()), 
                                'start_time':new Date(line.timer_starttime), 
                                'table_id':line.order.table ? line.order.table.id : '',
                                'current_screen': self.pos.config.id,
                                'screen_name': self.pos.config.name}).then(function(results){
                            });                            
                        }
                    }
                }
            }
            
            var kitchen_order_history = $(qweb.render('KitchenOrders', {
                widget: this,
            }));
            kitchen_order_history =  $(kitchen_order_history)
            kitchen_order_history.appendTo(this.$('.subwindow-container-fix-kitchen'))
            
            this.$('.done-all').click(function () {
                var line_id = $(this).data()['id'];
                var line = self.pos.get_line_by_uid(line_id);
                    if(!line){
                        line = self.pos.get_pack_line_by_uid(line_id)
                    }
                if(line){
                    line.stopTimer();
                    var ended_time = $('span#sw_'+line.uid+'_h').text() + ':' + $('span#sw_'+line.uid+'_m').text() + ':' + $('span#sw_'+line.uid+'_s').text() + ':' + $('span#sw_'+line.uid+'_ms').text();
                    var order_line = JSON.stringify(line.export_as_JSON());
                    // var order_id = order.id;
                    var a = ended_time.split(':'); // split it at the colons
                    var total_seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]) + (+a[3])/1000; 
                    new Model("order.history").call("update_orders", [order.uid, line.uid, total_seconds,new Date(Date.now()), self.pos.config.id],).then(function(results){
                    });
                    if(line.product.pos_categ_id && line.product.pos_categ_id[0] in self.pos.next_screen_by_categ){
                        line.next_screen = self.pos.next_screen_by_categ[line.product.pos_categ_id[0]]
                    }else{
                        line.next_screen = false
                        line.completion_time = new Date(Date.now())
                    }

                    if(line.total_seconds && line.total_seconds>0){
                        total_seconds = line.total_seconds + total_seconds
                    }
                    console.log('line.summary_screen  '+line.summary_screen)
                    self.pos.pos_bus.push_message_to_other_sessions({
                        action: 'sync_next_screen',
                        data: {
                            uid: line.uid,
                            next_screen: line.next_screen,
                            summary_screen: line.summary_screen,
                            total_seconds: total_seconds,
                            timer_starttime: Date.now(),
                            order_confirm_date: order.confirmation_time || new Date().getTime()
                        },
                        order: line.order.export_as_JSON(),
                        bus_id: self.pos.config.bus_id[0],
                    });
                    if($(this).parents('.branch-line').find('.product-line').length<=1){
                        if($(this).parents('#table_order').find('.branch-line').length==1){
                            $(this).parents('#table_order').remove()
                        }else{
                            $(this).parents('.branch-line').remove()
                        } 

                    }else{
                        $(this).parents('.product-line').remove()
                    }                           
                }
            });
            
            $('#tborder').click(function() {
                $('#ordhist').removeClass('active');
                $(this).addClass("active");
                $('.ohistory').hide();
                $('.client-card').show();
            });
            $('#ordhist').click(function() {
                $('#tborder').removeClass('active');
                $(this).addClass("active");
                $('.client-card').hide();
                $('.ohistory').show();
                var contents = document.querySelector('.order-list-contents');
                contents.innerHTML = "";
                new Model("order.history").call("get_history", [self.pos.config.id],).then(function(res){
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
        },
    });
    gui.define_screen({
        'name': 'kitchen_screen',
        'widget': KitchenScreenWidget,
    });
  

});
