odoo.define('pos_startscreen.screens', function (require) {
"use strict";

var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var floors = require('pos_restaurant.floors');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');

var _t = core._t;



screens.OrderWidget.include({
        renderElement: function(scrollbottom){
            this._super(scrollbottom);
            //$('div.service-charge-button').remove();
            $('button.done_all_btn').remove();
            $('button.send_kitchen').addClass('oe_hidden');
            $('button.exit_priority_btn').remove();
            $('button.high_priority').remove();
        }
    });

var OptionsPopupWidget = PopupWidget.extend({
    template: 'OptionsPopupWidget',
    events: _.extend({}, PopupWidget.prototype.events, {
        'click .close_session':  'close_session_click',
        'click .dinein_btn':  'show_dinein_screen',
        'click .takeaway_btn':  'show_takeaway_screen',
        'click .staffmeal_btn':  'show_staffmeal_screen',
        'click .delivery_btn':  'show_delivery_screen',
        'click .transferout_btn':  'show_transferout_screen',
    }),
    show: function(options){
        options = options || {};
        this._super(options);
        this.pos.config.iface_floorplan = 1;
    },
    close_session_click : function () {
        this.gui.close();
    },
    show_dinein_screen : function () {
        this.pos.category = 'dine_in';
        this.pos.config.iface_floorplan = 1;
        this.gui.show_screen('floors')
    },
    show_takeaway_screen : function () {
        this.pos.category = 'take_away';
        this.pos.config.iface_floorplan = 0;
        if(!this.pos.get_order()) this.pos.add_new_order();
        this.gui.show_screen('products');
    },
    show_staffmeal_screen : function () {
        this.pos.category = 'staff_meal';
        this.pos.config.iface_floorplan = 0;
        if(!this.pos.get_order()) this.pos.add_new_order();
        this.gui.show_screen('products');
    },
    show_delivery_screen : function () {
        this.pos.category = 'delivery';
        this.pos.config.iface_floorplan = 0;
        if(!this.pos.get_order()) this.pos.add_new_order();
        this.gui.show_screen('products');
    },
    show_transferout_screen : function () {
        this.pos.category = 'transfer_out';
        this.pos.config.iface_floorplan = 0;
        if(!this.pos.get_order()) this.pos.add_new_order();
        this.gui.show_screen('products');
    }
});
gui.define_popup({name:'optionpopup', widget: OptionsPopupWidget});

//Floor screens
floors.FloorScreenWidget.include({
    show: function(){
        this._super();
        this.chrome.widget.order_selector.hide();
        if (!this.pos.table){
            this.gui.show_popup('optionpopup', {
                'title': _t("LET'S GET STARTED"),
            });
        }
    },
});

//Chrome
chrome.Chrome.include({

    build_chrome: function() {
        this._super();
        var self = this;
        if(self.pos.config.screen_type=='e_menu'){
            $('.back_home_screen_button').text('Clear');
            $('.back_home_screen_button').click(function(){
                var orderlines = self.pos.get_order().orderlines;
                while (orderlines.length>0){
                    orderlines.remove(orderlines.models[0].id);
                }
            });
        }else{
            $('.back_home_screen_button').click(function(){
                $('.assign-order').addClass('oe_hidden');
                self.gui.screen_instances.products.$('.pay').off().click(function(){
                    var order = self.pos.get_order();
                    var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                        return line.has_valid_product_lot();
                    });
                    if(!has_valid_product_lot){
                        self.gui.show_popup('confirm',{
                            'title': _t('Empty Serial/Lot Number'),
                            'body':  _t('One or more product(s) required serial/lot number.'),
                            confirm: function(){
                                self.gui.show_screen('payment');
                            },
                        });
                    }else{
                        self.gui.show_screen('payment');
                    }
                });
                self.gui.show_popup('optionpopup', {
                    'title': _t("LET'S GET STARTED"),
                });
            });
        }
    },
});
return OptionsPopupWidget;
});

