odoo.define('complex_kds.summary_screen', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    var SummaryScreenWidget = screens.ScreenWidget.extend({
        template: 'SummaryScreenWidget',
        show_numpad: false,
        show_leftpane: true,
        previous_screen: false,
        start: function () {
            var self = this;
            this._super();
            this.pos.bind('update:summaryscreen', function () {
                self.renderElement();
            });
        },
        show: function () {
            var self = this;
            this._super();
        },
        renderElement: function () {
            var self = this
            this._super();
            this.$('.subwindow-container-fix-summary').html('')
            var self = this;
            var items = [];
            var orders_kanban = [];
            var orders_kanban_splitted = [];
            if (this.pos.config.screen_type == 'manager') {
                console.log('this is future for manager control all system');
                return;
            } else if(this.pos.config.screen_type == 'summary'){
                $('.username').hide();
                $('.order-selector').hide();
                $('.pos-screenname').text(self.pos.config.name)
                // var orders = this.pos.get('orders').models;
                var orders = []
                for (var i = this.pos.get('orders').models.length - 1; i >= 0; i--) {
                    console.log("this.pos.get('orders').models[i].confirmation_time    ",this.pos.get('orders').models[i].confirmation_time)
                    if(this.pos.get('orders').models[i].confirmation_time){orders.push(this.pos.get('orders').models[i])}
                }
                orders = orders.sort(function(a,b){return new Date(a.confirmation_time).getTime() - new Date(b.confirmation_time).getTime()});
                console.log('Orders   :::    ',orders)
                var order = null;
                var categs = [];
                if (orders.length <= 0) {
                    console.error('Order is empty');
                    return;
                }
                for (var i = 0; i < orders.length; i++) {
                    orders_kanban.push([])
                    orders_kanban_splitted.push([])
                }
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];

                    if(!orders_kanban[i]){
                        orders_kanban[i].push(order)
                    }
                    if(!orders_kanban[i]){
                        orders_kanban_splitted[i].push(order)
                    }
                    for (var j = order.orderlines.models.length -1; j >=0 ; j--) {
                        var line = order.orderlines.models[j];
                        console.log('State : '+line.state +"  ---------------------------------------------");
                        console.log('Summary screen   ',line.summary_screen, self.pos.config.id)
                        if (line.state == 'Done') {
                            console.log('state is DONE, pass');
                            continue;
                        }
                        if (line.state == 'Need-to-confirm') {
                            console.log('State : '+line.state +"  So it is passed");
                            continue;
                        }
                        if(line.summary_screen && line.summary_screen[0] == self.pos.config.id && !line.is_pack){
                            if (line.popup_option==order.popup_option) {
                                orders_kanban[i].push(line);
                            }else{
                                orders_kanban_splitted[i].push(line);
                            }
                        }
                        if(line.is_pack){
                            for (var k = order.pack_product_lines.length - 1; k >= 0; k--) {
                                    var l= order.pack_product_lines.models[k]
                                    l.parent_pack_name = line.product.display_name
                                    if(l.summary_screen && l.summary_screen[0] == self.pos.config.id && l.main_pack_line==line.uid){
                                        if (line.popup_option==order.popup_option) {
                                            orders_kanban[i].push(l);
                                        }else{
                                            orders_kanban_splitted[i].push(l);
                                        }
                                    }
                                }
                        }
                    }
                }
            
            this.orders_kanban = orders_kanban
            this.$('.subwindow-container-fix-summary').html('')
            orders_kanban = orders_kanban.concat(orders_kanban_splitted)
            console.log('orders_kanban',orders_kanban)

            for (var i in orders_kanban) {
                console.log('orders_kanban[i]   ',orders_kanban[i])
                if(orders_kanban[i].length>0){
                    
                    // for (var i = orders_kanban[item].length - 1; i >= 0; i--) {
                        var total_seconds_order = 0
                        var group_by_categ = {}
                        var table = ''
                        var floor = ''
                        var order = false
                        for (var j = orders_kanban[i].length - 1; j>= 0; j--) {
                            var line = orders_kanban[i][j]
                            // var floor = line.order.table ? line.order.table.floor.name : ''
                            // var table = line.order.table ? line.order.table.name : ''
                            order = line.order
                            if(line.product.pos_categ_id && !(line.product.pos_categ_id in group_by_categ)){
                                group_by_categ[line.product.pos_categ_id] = [line]
                            }else{
                                group_by_categ[line.product.pos_categ_id].push(line)
                            } 
                            var background_color = 'white'
                            var font_color = 'black'
                            if(line.total_seconds && !line.next_screen && !line.is_pack){
                                // total_seconds_order += line.total_seconds
                                var hours = Math.floor(line.total_seconds / (60 * 60));

                                var divisor_for_minutes = line.total_seconds % (60 * 60);
                                var minutes = Math.floor(divisor_for_minutes / 60);

                                var divisor_for_seconds = divisor_for_minutes % 60;
                                var seconds = Math.ceil(divisor_for_seconds);
                                line.format_time = hours +':'+minutes +':'+ seconds
                                var normaltime = line.product.normal_time_cook
                                var total_seconds = line.total_seconds/line.get_quantity()
                                if(normaltime < total_seconds){
                                    if(((normaltime)+(normaltime*10/100))>=total_seconds){
                                        background_color = 'yellow'
                                    }else{
                                        background_color = 'red'
                                        font_color='white'
                                    }
                                }else{
                                    background_color = '#66FF66'
                                    font_color='black'
                                }
                            }
                            line.background_color = background_color
                            line.font_color = font_color                        
                        }
                        
                        if(orders_kanban[i].length>0){
                            console.log('line.popup_option ? line.popup_option : line.order.popup_option  ',line.popup_option ? line.popup_option : line.order.popup_option)
                            var summary_line = $(qweb.render('SummaryKanban', {
                            widget: this,
                            done_lines:  [i],
                            total_time: hours +':'+minutes,
                            total_seconds:total_seconds_order,
                            group_by_categ: group_by_categ,
                            floor:line.order.table ? line.order.table.floor.name : '',
                            table:line.order.table ? line.order.table.name : '',
                            line_done:line,
                            order:order,
                            popup_option:line.popup_option ? line.popup_option : line.order.popup_option,
                            customer: order.get_client(),
                            }));
                            $(summary_line).appendTo(this.$('.subwindow-container-fix-summary'))
                            console.log('appendedddd'+this.$('.subwindow-container-fix-summary').length)
                            order.startTimer('sw_'+order.uid,order.confirmation_time)
                        }
                       for (var item in group_by_categ) {
                            for (var i = group_by_categ[item].length - 1; i >= 0; i--) {
                                var l = group_by_categ[item][i]
                                l.startTimer('sw_'+l.uid, l.creation_date, true)
                            }
                        }           
                }
            }
            }
            this.$('.done-all').click(function () {
                var line_id = $(this).data()['id'];
                var done_line = self.pos.get_line_by_uid(line_id);
                    if(!done_line){
                        done_line = self.pos.get_pack_line_by_uid(line_id)
                    }
                var orders = self.pos.get('orders').models;
                var done_order = self.pos.get_order_by_uid(done_line.order.uid);
                var has_next = false
                for (var j = 0; j < done_order.orderlines.models.length; j++) {
                    var line = done_order.orderlines.models[j]
                    if(line.summary_screen && line.summary_screen[0]==self.pos.config.id && line.next_screen && line.popup_option==done_line.popup_option && !line.is_pack){
                        has_next = true
                    }else if(line.is_pack){
                        for (var k = done_order.pack_product_lines.length - 1; k >= 0; k--) {
                            var l= done_order.pack_product_lines.models[k]
                            if(l.summary_screen && l.summary_screen[0]==self.pos.config.id && l.next_screen && l.popup_option==done_line.popup_option && l.main_pack_line==line.uid){
                                has_next = true
                            }
                        }
                    }
                }
                if(has_next){
                    alert('Products are still cooking...')
                }
                if(!has_next){
                    done_order.stopTimer()
                    var ended_time = $('span#sw_'+done_order.uid+'_h').text() + ':' + $('span#sw_'+done_order.uid+'_m').text() + ':' + $('span#sw_'+done_order.uid+'_s').text() + ':' + $('span#sw_'+done_order.uid+'_ms').text();
                    var a = ended_time.split(':'); // split it at the colons
                    var total_seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]) + (+a[3])/1000;        
                    for (var j = 0; j < done_order.orderlines.models.length; j++) {
                        var line = done_order.orderlines.models[j]
                        if(done_order.remove_from_summary && done_order.popup_option!='Take Away'){
                            done_order.remove_from_summary = false
                            done_order.finalize()
                        }else if(line.summary_screen && line.summary_screen[0]==self.pos.config.id && line.popup_option==done_line.popup_option && !line.pack){
                            line.summary_screen = false
                                self.pos.pos_bus.push_message_to_other_sessions({
                                action: 'sync_next_screen',
                                data: {
                                    uid: line.uid,
                                    next_screen: false,
                                    summary_screen: false,
                                    total_seconds: line.total_seconds,
                                    ended_time:ended_time,
                                    completion_time: Date.now()
                                },
                                order: line.export_as_JSON(),
                                bus_id: self.pos.config.bus_id[0],
                                });
                        }else if(line.is_pack){
                                for (var k = done_order.pack_product_lines.length - 1; k >= 0; k--) {
                                    var l= done_order.pack_product_lines.models[k]
                                    if(l.summary_screen && l.summary_screen[0]==self.pos.config.id && line.popup_option==done_line.popup_option && l.main_pack_line==line.uid){
                                            l.summary_screen = false
                                            self.pos.pos_bus.push_message_to_other_sessions({
                                            action: 'sync_next_screen',
                                            data: {
                                                uid: l.uid,
                                                next_screen: false,
                                                summary_screen: false,
                                                total_seconds: l.total_seconds,
                                                ended_time:ended_time,
                                                completion_time: Date.now()
                                            },
                                            order: l.order.export_as_JSON(),
                                            bus_id: self.pos.config.bus_id[0],
                                            });
                                        }
                                }
                        }
                    }
                    if(done_order.popup_option=='Delivery'){
                        new Model('pos.sales.order').call('confirm_sale', [done_order.uid]).then(function(result){});
                    }
                    new Model("order.history").call("manage_order_history", [], {
                                'order':JSON.stringify(done_order.export_as_JSON()), 
                                'start_time':new Date(done_order.confirmation_time), 
                                'table_id':done_order.table ? done_order.table.id : '',
                                'current_screen': self.pos.config.id,
                                'screen_name': self.pos.config.name,
                                'duration':total_seconds,
                                'end_time':new Date(Date.now()),}).then(function(results){
                            });
                    self.renderElement()  
                }

            });

            
        },
    });
    gui.define_screen({
        'name': 'summary_screen',
        'widget': SummaryScreenWidget,
    });
});