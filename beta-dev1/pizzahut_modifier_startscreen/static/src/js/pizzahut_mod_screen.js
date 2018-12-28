odoo.define('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen', function (require) {
"use strict";

var PosBaseWidget = require('point_of_sale.BaseWidget');
var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var floors = require('pos_restaurant.floors');
var core = require('web.core');
var Model = require('web.DataModel');
var PopupWidget = require('point_of_sale.popups');


var QWeb = core.qweb;
var _t = core._t;

    models.load_models({
        model: 'restaurant.floor',
        fields: ['name','background_color','table_ids','sequence','pos_config_ids'],
        domain: function(self){ return [['pos_config_ids','in',self.config.id]]; },
        loaded: function(self,floors){
            self.floors = floors;
            self.floors_by_id = {};
            for (var i = 0; i < floors.length; i++) {
                floors[i].tables = [];
                self.floors_by_id[floors[i].id] = floors[i];
            }

            // Make sure they display in the correct order
            self.floors = self.floors.sort(function(a,b){ return a.sequence - b.sequence; });

            // Ignore floorplan features if no floor specified.
            self.config.iface_floorplan = !!self.floors.length;
        },
    },{'after': 'restaurant.floor'});
    
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            _super_posmodel.initialize.call(this, session, attributes);
            this.category = '';
        },

    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            var res = _super_order.initialize.apply(this, arguments);
            this.category = this.pos.category;
            return res;
        },
    });

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
        }),
        show: function(options){
            options = options || {};
            this._super(options);
            this.pos.config.iface_floorplan = 1;
        },
        close_session_click : function () {
        	this.gui.close();
        }
    });
    gui.define_popup({name:'optionpopup', widget: OptionsPopupWidget});

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

