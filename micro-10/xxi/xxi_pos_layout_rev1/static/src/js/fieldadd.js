odoo.define('xxi_pos_layout.fieldadd', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var screens = require('point_of_sale.screens');
var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var QWeb = core.qweb;

models.load_fields('pos.config',['new_interface']);

chrome.Chrome.include({

        build_chrome: function () {
            this._super();
            var today = new Date();
            var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            var date = days[today.getDay()]+ '  ' + today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
            var time = today.getHours() + ":" + today.getMinutes();
            var dateTime = date+' '+time;
            this.pos['current_date'] = dateTime
        },
    });


var ClientListScreenWidget = screens.ClientListScreenWidget.extend({
    template: 'ClientListScreenWidget',
    save_changes: function(){
        var self = this;
        this._super();
        var current_order = this.pos.get_order();
        current_order.customer_note_name = this.new_client.name
    },
});

gui.define_screen({name:'clientlist', widget: ClientListScreenWidget});

var ReceiptScreenWidget = screens.ReceiptScreenWidget.extend({
    template: 'ReceiptScreenWidget',
    click_next: function() {
        var self = this;
        this._super();
        $( ".customer_name" ).remove();
        $('.pos-branding').append('<span class="customer_name"></span>');
    },
});

gui.define_screen({name:'receipt', widget: ReceiptScreenWidget});

return {
	ClientListScreenWidget: ClientListScreenWidget,
	ReceiptScreenWidget: ReceiptScreenWidget,
};
});