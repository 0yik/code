odoo.define('takeaway_screen.chrome', function (require) {

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    chrome.Chrome.include({
        build_widgets: function () {
            this._super();
            // alert('this.pos.config.screen_type' +this.pos.config.screen_type)
            if (this.pos.config.screen_type && this.pos.config.screen_type == 'takeaway') {
                this.gui.set_startup_screen('takeaway');
                // alert('hellooooooooooooooooo')
                this.gui.set_default_screen('takeaway');
                // this.gui.current_screen = 'summary_screen'
                this.$('.username').hide();
                $('.order-selector').hide();
            }
        },
    });
});