odoo.define('takeaway_screen.takeaway_screen', function (require) {
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

    var TakeAwayWidget = screens.ScreenWidget.extend({
        template: 'TakeAwayScreenWidget',
        show_numpad: false,
        show_leftpane: true,
        previous_screen: false,
        start: function () {
            var self = this;
            this._super();
            this.pos.bind('update:takeaway', function () {
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
            console.log('All Orders'+this.pos.get('orders').models.length)
            this.$('.subwindow-container-fix-takeaway').html('')
            var self = this;
            var items = [];
            var orders_kanban = [];
            var orders_kanban_splitted = [];
            if (this.pos.config.screen_type == 'manager') {
                console.log('this is future for manager control all system');
                return;
            } else if(this.pos.config.screen_type == 'takeaway'){
                $('.username').hide();
                $('.order-selector').hide();
                $('.pos-screenname').text(self.pos.config.name)
                var orders = this.pos.get('orders').models;
                orders = orders.sort(function(a,b){return new Date(a.confirmation_time).getTime() - new Date(b.confirmation_time).getTime()});
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
                    console.log('POP UP OPTIOn   ',order.popup_option)
                    var cont = false
                    if(!orders_kanban[i]){
                        orders_kanban[i].push(order)
                    }
                    if(!orders_kanban[i]){
                        orders_kanban_splitted[i].push(order)
                    }
                    for (var j = order.orderlines.models.length -1; j >=0 ; j--) {
                    var line = order.orderlines.models[j];
                    console.log('line.takeaway_screenline.takeaway_screen   '+line.popup_option+line.takeaway_screen+'[[[[[[[[[[[[    '+self.pos.config.id)
                        if (line.state == 'Done') {
                            console.log('state is DONE, pass');
                            continue;
                        }
                        if (line.state == 'Need-to-confirm') {
                            console.log('Need-to-confirm, pass');
                            continue;
                        }
                        if(line.takeaway_screen && line.takeaway_screen[0] == self.pos.config.id){
                            if (line.popup_option=='dive_in_take_away' || line.popup_option=='Take Away') {
                                console.log('Take Away I n loop')
                                orders_kanban[i].push(line);
                            }
                        }
                    }
                }
            
            this.orders_kanban = orders_kanban
            this.$('.subwindow-container-fix-takeaway').html('')
            orders_kanban = orders_kanban.concat(orders_kanban_splitted)

            for (var i in orders_kanban) {
                if(orders_kanban[i].length>0){
                        // var total_seconds_order = 0
                        var group_by_categ = {}
                        var table = ''
                        var floor = ''
                        var order = false
                        var done_order = true
                        var completion_time = false
                        var ended_time = false
                        for (var j = orders_kanban[i].length - 1; j>= 0; j--) {
                            var line = orders_kanban[i][j]
                            order = line.order
                            console.log('>>>>>>         ',line.summary_screen)
                            console.log('4444444444     ',line.next_screen)
                            console.log(';;;;;          ', line.completion_time)
                            if(line.summary_screen || line.next_screen || !line.completion_time){
                                done_order = false
                            }
                            if(line.completion_time){
                                if(!completion_time){
                                    completion_time = new Date(line.completion_time)
                                }else{
                                    if(new Date(line.completion_time) > completion_time){
                                        completion_time = line.completion_time
                                    }
                                }
                                ended_time = line.ended_time
                            }
                        }
                        if(orders_kanban[i].length>0){
                            if(done_order && !order.timer){
                                var countDownDate = new Date(completion_time).getTime()
                                order.set_interval_20(countDownDate)
                                // Update the count down every 1 second
                                // order.timer = setInterval(function() {
                                //     console.log('>>>    UID  ',order.uid)

                                //     // Get todays date and time
                                //     var now = new Date().getTime();
                                    
                                //     // Find the distance between now an the count down date
                                //     var distance = now - countDownDate;
                                //     console.log('distance   ',distance/1000)
                                    
                                //     if (distance > 120000) {
                                //         console.log('inside', order.uid)
                                //         order.remove_from_summary = false
                                //         order.finalize()
                                //         $('tr#'+order.uid).remove()
                                //         clearInterval(order.timer);
                                //     }
                                // }, 3000);                                
                            }
                            console.log('order.get_client()   ',order.get_client())
                            console.log('done_order  ',done_order)
                            var takeaway_line = $(qweb.render('TakeAwayKanban', {
                            widget: this,
                            order:order,
                            state: done_order ? 'Done' : 'Processing',
                            date: order ? new Date(order.confirmation_time).toTimeString().split(' ')[0] : '',
                            customer: order.get_client(),
                            }));
                            console.log('[yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy   ',$('.order-list-contents-takeaway').length)
                            $(takeaway_line).appendTo($('.order-list-contents-takeaway'))
                        }
                }
            }
            }
                       
        },
    });
    gui.define_screen({
        'name': 'takeaway',
        'widget': TakeAwayWidget,
    });
});