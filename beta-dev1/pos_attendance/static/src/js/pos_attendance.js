odoo.define('pos_attendance', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require("point_of_sale.popups");
    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var Model = require('web.Model');
    var round_pr = utils.round_precision;

    var attendance_popup = PopupWidget.extend({
        template: 'attendance_popup',
        events: {
            "click .button_confirm_attendance": function() {
                this.create_attendance();
            },
            'click .button.cancel':  'click_cancel',
        },
        click_cancel: function(){
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
            }
        },

        init: function (parent, options) {
            this._super(parent, options);
            this.current_popup  = null;
        },
        
        renderElement: function () {
            var order = this.pos.get_order();
            this._super();
        },

        create_attendance: function () {
            var self = this;
            var login = $("#login").val()
            var password = $("#password").val()
            new Model('hr.attendance').call('create_attendance', [[], password, login]).then(function(result) {
            	if (result.warning){
            		self.gui.show_popup('error', {
                        title: _t(result.title),
                        body: _t(result.warning),
                    });
            	}
            	else {
//	            	self.$el.addClass('oe_hidden');
//	            	$('.check_out_attendance').removeClass("oe_hidden");
	            	self.gui.show_popup('welcome_popup', {
	            		title: _t('Success!!'),
	            		user: _t(result.user),
	            		check_time: _t(result.check_time),
	            		action : _t(result.action),
	            		msg : _t(result.msg),
	            	});
            	}
            });
        },

    })
    gui.define_popup({
        name: 'attendance_popup',
        widget: attendance_popup
    });


    var attendance_button = screens.ActionButtonWidget.extend({
        template: 'attendance_button',
        button_click: function () {
        	var self = this
        	self.gui.show_popup('attendance_popup');
        },
    });

    screens.define_action_button({
        'name': 'attendance_button',
        'widget': attendance_button,
    });

    var welcome_popup = PopupWidget.extend({
        template: 'welcome_popup',
        init: function (parent, options) {
            this._super(parent, options);
        },
        
        renderElement: function () {
            this._super();
        },


    })
    gui.define_popup({
        name: 'welcome_popup',
        widget: welcome_popup
    });

});
