odoo.define('barcode_kiosk.barcode_kiosk', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var Session = require('web.session');
var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');

var QWeb = core.qweb;
var _t = core._t;
var emp_id = false;


var BarcodeKiosk = Widget.extend(BarcodeHandlerMixin, {
    events: {
        "click .o_hr_button_barcode_kiosk": function(event){
			event.preventDefault();
			if (emp_id != false){
				this.do_action('hr_barcode_kiosk_scan')}
			},
			
		"change .o_badge_id": '_check_badge_id',
    },
	
	_check_badge_id : function(event){
		event.preventDefault();
		var self = this
		var badge = $('.o_badge_id').val()
		ajax.jsonRpc('/check_badge', 'call', {badge}, ).then(function (result) {
			emp_id = result;
			if (result == false){
				alert("Badge does not exists");
				event.preventDefault();
				event.stopPropagation();
				return false;
			}
		});
	},
	
    init: function (parent, action) {
        // Note: BarcodeHandlerMixin.init calls this._super.init, so there's no need to do it here.
        // Yet, "_super" must be present in a function for the class mechanism to replace it with the actual parent method.
        this._super;
        BarcodeHandlerMixin.init.apply(this, arguments);
    },

    start: function () {
        var self = this;
        self.session = Session;
        var res_company = new Model('res.company');
        res_company.query(['name'])
           .filter([['id', '=', self.session.company_id]])
           .all()
           .then(function (companies){
                self.company_name = companies[0].name;
                self.$el.html(QWeb.render("HrBarcodeKiosk", {widget: self}));
            });
        return self._super.apply(this, arguments);
    },

    on_barcode_scanned: function(barcode) {
        var self = this;
        var hr_employee = new Model('hr.employee');
        hr_employee.call('attendance_scan', [barcode, ])
            .then(function (result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
    },

});

core.action_registry.add('hr_barcode_kiosk', BarcodeKiosk);



var MainMenu = Widget.extend(BarcodeHandlerMixin, {
	
    template: 'main_menu',
    events: {
        "click .button_stock_in": function(){ this.open_stock_in() },
        "click .button_stock_out": function(){ this.open_stock_out() },
		"click .button_stock_take": function(){ this.open_inventory() },
    },

    init: function(parent, action) {
        // Note: BarcodeHandlerMixin.init calls this._super.init, so there's no need to do it here.
        // Yet, "_super" must be present in a function for the class mechanism to replace it with the actual parent method.
        this._super;
        BarcodeHandlerMixin.init.apply(this, arguments);
        this.message_demo_barcodes = action.params.message_demo_barcodes;
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            if (self.message_demo_barcodes) {
                self.setup_message_demo_barcodes();
            }
        });
    },

    on_attach_callback: function() {
        this.start_listening();
    },

    on_detach_callback: function() {
        this.stop_listening();
    },

    on_barcode_scanned: function(barcode) {
        var self = this;
		
        Session.rpc('/barcode_kiosk/scan_from_main_menu', {
            barcode: barcode,
        }).then(function(result) {
            if (result.action) {
                self.do_action(result.action);
            } else if (result.warning) {
                self.do_warn(result.warning);
            }
        });
    },

    open_stock_out: function() {
        var self = this;
        return new Model("stock.picking")
            .call("open_stock_out_picking", [emp_id])
            .then(function(result) {
                self.do_action(result);
            });
    },
	open_stock_in: function() {
        var self = this;
        return new Model("stock.picking")
            .call("open_stock_in_picking", [emp_id])
            .then(function(result) {
                self.do_action(result);
            });
    },
	open_inventory: function() {
        var self = this;
        return new Model("stock.inventory")
            .call("open_new_inventory", [])
            .then(function(result) {
                self.do_action(result);
            });
    },

});

core.action_registry.add('hr_barcode_kiosk_scan', MainMenu);
return BarcodeKiosk;
return {
    MainMenu: MainMenu,
};

});
