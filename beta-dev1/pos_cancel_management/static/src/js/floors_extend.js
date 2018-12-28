odoo.define('pos_cancel_management.floors_extend', function (require) {
"use strict";

    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var QWeb = core.qweb;
    var _t = core._t;
    var _super_order = models.Order.prototype;
    var floors = require('pos_restaurant.floors');
    models.Order = models.Order.extend({
        build_line_resume: function(){
            var resume = {};
            this.orderlines.each(function(line){
                if (line.mp_skip) {
                    return;
                }
                var line_hash = line.get_line_diff_hash();
                var qty  = Number(line.get_quantity());
                var note = line.get_note();
                var cancel_order_reason = line.get_cancel_order_reason();
                var product_id = line.get_product().id;

                if (typeof resume[line_hash] === 'undefined') {
                    resume[line_hash] = {
                        qty: qty,
                        note: note,
                        cancel_order_reason: cancel_order_reason,
                        product_id: product_id,
                        product_name_wrapped: line.generate_wrapped_product_name(),
                    };
                } else {
                    resume[line_hash].qty += qty;
                }

            });
            return resume;
        },
        saveChanges: function(){
            this.saved_resume = this.build_line_resume();
            this.orderlines.each(function(line){
                line.set_dirty(false);
            });
            this.trigger('change',this);
        },
        printChanges: function(){
            var printers = this.pos.printers;
            for(var i = 0; i < printers.length; i++){
                var changes = this.computeChanges(printers[i].config.product_categories_ids);
                if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
                    var receipt = QWeb.render('OrderChangeReceipt',{changes:changes, widget:this});
                    printers[i].print(receipt);
                }
            }
        },
        hasChangesToPrint: function(){
            var printers = this.pos.printers;
            for(var i = 0; i < printers.length; i++){
                var changes = this.computeChanges(printers[i].config.product_categories_ids);
                if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
                    return true;
                }
            }
            return false;
        },
        hasSkippedChanges: function() {
            var orderlines = this.get_orderlines();
            for (var i = 0; i < orderlines.length; i++) {
                if (orderlines[i].mp_skip) {
                    return true;
                }
            }
            return false;
        },
    });

    
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        set_cancel_order_reason: function(cancel_order_reason){
            this.cancel_order_reason = cancel_order_reason;
            // this.trigger('change',this);
        },
        get_cancel_order_reason: function(cancel_order_reason){
            return this.cancel_order_reason;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_cancel_order_reason() !== this.get_cancel_order_reason()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.cancel_order_reason = this.cancel_order_reason;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.cancel_order_reason = this.cancel_order_reason;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.cancel_order_reason = json.cancel_order_reason;
        },
    });
    
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        process_cancel_order: function(order, line, opertion=''){
            if (opertion == 'delete'){
                line.set_quantity('remove')
                return true;
            }
            var res = confirm("You are going to cancel this item, confirm?");
            if (res && opertion == 'cancel'){
                var cancel_order_reason = prompt("Please, input reason for cancel order.");
                if(cancel_order_reason){
                    if (line.state != 'Cancelled' && line.state != 'Done' && line.state != 'Error') 
                    {
                        this.gui.show_popup('number', {
                            'title':  _t('Enter PIN Number'),
                            'cheap': true,
                            'value': '',
                            'confirm': function(value) {
                                if(!value){
                                    alert('Please Enter PIN First!')
                                    return
                                }
                                var user = this.pos.get_cashier();
                                var pin = $('.popup-input').text();
                                var username = $('.username')
                                var model = new Model('res.users');
                                var user_id = this.pos.user.id;
                                if(this.pos.check_pin_number(pin)){
                                    line.set_state('Cancelled');
                                    line.set_cancel_order_reason(cancel_order_reason);
                                    line.set_quantity(0);
                                }else{
                                    alert("You have entered a wrong PIN")
                                }
                                // model.call("compare_pin_number", [pin]).then(function (result) {
                                //     if (result){
                                //         line.set_state('Cancelled');
                                //         line.set_cancel_order_reason(cancel_order_reason);
                                //         line.set_quantity(0);
                                //     }
                                //     else{
                                //         alert("You have entered a wrong PIN")
                                //     }
                                // });
                            },
                        });
                    }
                }
                else{
                    alert("Please input the cancel reason. try again.");
                }
            }
        },
    });
  
    var CancelOrderButton = screens.ActionButtonWidget.extend({
        template: 'CancelOrderButton',
        button_click: function() {
        var self = this;
        var user = this.pos.user.id
        var order = this.pos.get_order();
        var line = this.pos.get_order().get_selected_orderline();
        if(!line){
            alert('There is no order line selected !');
            return;
        }
        if(line.state == 'Need-to-confirm'){
            this.pos.process_cancel_order(order, line, 'delete');

        }
        else if (line.state == 'Cancelled'){
            alert("Already Cancelled Order.");
        }
        else if (line.state == 'Done'){
            alert("Already Done Order.");
        }
        else if (line.state == 'Error'){
            alert("Please, check some error in order.");
        }
        else{
            this.pos.process_cancel_order(order, line, 'cancel');
        }
    },
    });

    screens.define_action_button({
        'name': 'CancelOrderButton',
        'widget': CancelOrderButton
    });

    screens.ProductScreenWidget.include({
        start: function(){ 
            var self = this;
            this._super();
            this.$('.control-buttons').find('cancel-orderline-button').first().appendTo( this.$('.control-buttons').parent().find('.control-buttons-section')  );
            this.$('.control-buttons').find('.order-submit').first().appendTo( this.$('.control-buttons').parent().find('.control-buttons-section')  );

            // for(var i=0; i < this.$('.control-buttons').find('.cancel-orderline-button').length; i++){
            //     this.$('.control-buttons').find('.cancel-orderline-button').first().remove();
            // }
            for(var i=0; i < this.$('.control-buttons').find('.order-submit').length; i++){
                this.$('.control-buttons').find('.order-submit').first().remove();
            }
            this.$('.control-buttons').parent().find('.control-buttons-section').addClass('control-buttons');
            if(self.action_buttons['ButtonHighPriority']){
                self.action_buttons['ButtonHighPriority'].$el.off('click');
                self.action_buttons['ButtonHighPriority'].$el.on('click', function() {
                    var order = self.pos.get('selectedOrder');
                    if (order.orderlines.length > 0) {
                        for (var i = 0; i < order.orderlines.models.length; i++) {
                            var line = order.orderlines.models[i];
                            if (line.state != 'Kitchen confirmed cancel' && line.state != 'Done' && line.state != 'Cancel' && line.state != 'Error' && line.state != 'Waiting-delivery' && line.state != 'Cancelled') {
                                line.set_state('High-Priority');
                            }
                        }
                    }
                });
            }
                
        },

    });


});
