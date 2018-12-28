odoo.define('takeaway_screen.models', function (require) {

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
        model: 'category.mapping.line',
        fields: ['categ_ids', 'next_pos_config_id','ip_address','config_id',],
        domain: function(self){ return [['config_id3','=',self.config.id]]; },
        loaded: function(self, takeaway_mappings){
            self.takeaway_mappings =takeaway_mappings
            self.takeaway_by_categ = {}
            for (var i = 0; i < takeaway_mappings.length; i++) {
                for (var j = 0; j < takeaway_mappings[i].categ_ids.length; j++) {
                    self.takeaway_by_categ[takeaway_mappings[i].categ_ids[j]] = takeaway_mappings[i].next_pos_config_id;
                }
            }
        },
    });
    var PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        syncing_sessions: function(message) {
            PosModel.syncing_sessions.apply(this, arguments);
            if (this.config.screen_type == 'takeaway') {
                // alert('helloooo')
                this.trigger('update:takeaway');
            }  
        },
        sync_next_screen: function(vals) {
            PosModel.sync_next_screen.apply(this, arguments);
            var line = this.get_line_by_uid(vals['uid']);
            if (line) {
                line.syncing = true;
                line.next_screen = vals['next_screen'];
                line.summary_screen = vals['summary_screen'];
                this.play_sound();
                line.syncing = false;
                if('total_seconds' in vals){
                    line.total_seconds = vals['total_seconds']
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
                if('takeaway_screen' in vals){
                    line.takeaway_screen = vals['takeaway_screen']
                }
                if('ended_time' in vals){
                    line.ended_time = vals['ended_time']
                }
                if('completion_time' in vals){
                    line.completion_time = vals['completion_time']
                }
                // ended_time
            };
            this.trigger('update:kitchenscreen');
            this.trigger('update:summaryscreen');
            this.trigger('update:takeaway');
        },
    });
    var OrderLine = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({
        init_from_JSON: function(json) {
            this.takeaway_screen = json.takeaway_screen
            OrderLine.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function() {
            var loaded = OrderLine.export_as_JSON.apply(this, arguments);
            loaded.takeaway_screen = this.takeaway_screen
            return loaded;
        },
    });

    var Order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            var self = this
            Order.add_product.call(this, product, options);
            var line = this.get_selected_orderline()
            if((!options && line.product.pos_categ_id)){
                if(line.product.pos_categ_id[0] in self.pos.takeaway_by_categ){
                    line.takeaway_screen = self.pos.takeaway_by_categ[line.product.pos_categ_id[0]]
                }
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'sync_next_screen',
                    data: {
                        uid: line.uid,
                        next_screen: line.next_screen,
                        summary_screen: line.summary_screen,
                        popup_option: line.popup_option ? line.popup_option : line.order.popup_option,
                        takeaway_screen: line.takeaway_screen,
                        reward: line.reward,
                    },
                    order: line.export_as_JSON(),
                    bus_id: line.pos.config.bus_id[0],
                });
            }
            else if(options && options.next_screen){
                line.next_screen = options.next_screen
            }           
        },
        set_interval_20:function(countDownDate){
            var self = this
            this.timer = setInterval(function() {
                console.log('>>>    UID  ',self.uid)

                // Get todays date and time
                var now = new Date().getTime();
                
                // Find the distance between now an the count down date
                var distance = now - countDownDate;
                console.log('distance   ',distance/1000)
                
                if (distance > 120000) {
                    console.log('inside', self.uid)
                    self.remove_from_summary = false
                    self.finalize()
                    $('tr#'+self.uid).remove()
                    clearInterval(self.timer);
                }
            }, 3000); 

        }
    });
});