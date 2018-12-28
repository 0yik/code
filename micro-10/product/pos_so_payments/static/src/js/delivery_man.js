odoo.define('pos_so_payments.delivery_man', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var Model = require('web.DataModel');

    var DeliveryManPopupWidget = PopupWidget.extend({
        template: 'DeliveryManPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {

        }),
        init: function(parent, options){
            this._super(parent, options);
            this.parent_widget = false;
            this.deliver_list = [];
            var self = this;
            var employeeModel = new Model('hr.employee');
            var domain = [];
            var fields = ['id', 'name'];
            employeeModel.call('search_read', [domain, fields ])
                .then(function (result) {
                    console.log('employees: ', result);
                    self.deliver_list = result;
                }).fail(function (error, event) {
                    console.log(error, event);
                });
        },
        show: function(options){
            options = options || {};
            this._super(options);
            this.parent_widget = options.parent || false;
        },
        click_confirm: function(){
            var delivery_man = $('select.deliver_list').val();
            if(delivery_man){
                if(this.parent_widget){
                    this.parent_widget.validate_delivery_invoice(delivery_man);
                }
                this.gui.close_popup();
            }
            else{
                alert('Please enter delevery man');
                return;
            }
        },

    });

    gui.define_popup({name:'deliverymanpopup', widget: DeliveryManPopupWidget});
    return DeliveryManPopupWidget;
});