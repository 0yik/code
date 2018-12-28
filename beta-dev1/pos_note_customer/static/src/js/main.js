odoo.define('pos_note_customer.pos_open_customer', function (require) {
"use strict";
    var pos_model = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var popup_widget = require('point_of_sale.popups');
    var keyboard = require('point_of_sale.keyboard');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var SuperOrder = pos_model.Order;
    var _t = core._t;
    var QWeb = core.qweb;
    var gui = require('point_of_sale.gui');

    var popups = require('point_of_sale.popups')
    var PosBaseWidget = require('point_of_sale.BaseWidget');

var TextInputCustomerPopupWidget = popup_widget.extend({
    template: 'TextFieldCustomerPopupWidget',
    show: function(options){
        options = options || {};
        this._super(options);

        this.renderElement();
        this.chrome.widget.keyboard.connect(this.$('input'));
        this.$('input,textarea').focus();
    },
    click_confirm: function(){
        var value = this.$('input,textarea').val();
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,value);
        }
    },
});
gui.define_popup({name:'textinputcustomer', widget: TextInputCustomerPopupWidget});
    
screens.PaymentScreenWidget.include({
    renderElement: function() {
        var self = this;
        this._super();
        self.$('#customer_note').click(function(){
            self.gui.show_popup('textinputcustomer',{
                title: _t('Add Customer Name'),
                value:'',
                confirm: function(note) {
                    this.note = note;
                    var current_order = this.pos.get_order();
                    current_order.customer_note_name = note
                    self.$("#customer_note span").text(note);
                    console.log("======current_order.customer_note_name================",current_order,current_order.customer_note_name);
                },
            });
            
        });
    },
});

keyboard.OnscreenKeyboardWidget.include({
    deleteAllCharacters: function(){
        var input = this.$target[0];
        if($(input).attr('id') == 'customer_note_name'){
            input.dispatchEvent(this.generateEvent('keypress',{code: 8}));
            input.dispatchEvent(this.generateEvent('keyup',{code: 8}));
        }
        else{
            this._super()
        }
    },
})

});