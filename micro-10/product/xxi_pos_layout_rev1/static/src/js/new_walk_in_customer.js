odoo.define('xxi_pos_layout.new_walk_in_customer', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.Model');
var gui = require('point_of_sale.gui');
var multiprint = require('pos_restaurant.multiprint');
var Backbone = window.Backbone;
var QWeb = core.qweb;
var _t   = core._t;


var NewWalkInCustomerButton = screens.ActionButtonWidget.extend({
    template: 'NewWalkInCustomerButton',

    button_click: function(){
        var self = this;
        var line = this.pos.get_order().get_selected_orderline();
        if (line){
            this.gui.show_popup('textarea', {
                'title':  _t('Customer Name'),
                'cheap': true,
                'value':   line.get_note(),
                'confirm': function(value) {
                    $( ".customer_name" ).remove();
                    $('.pos-branding').append('<span class="customer_name">&nbsp;&nbsp;'+value+'</span>');
                    var current_order = this.pos.get_order();
                    current_order.customer_note_name = value
                },
            });
        }else{
            var warning = "Please select the menu first!";
            alert(warning);
        }
    },
});

screens.define_action_button({
    'name': 'New_Walk_In_Customer',
    'widget': NewWalkInCustomerButton,
});

});