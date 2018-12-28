odoo.define('complex_kds.gui', function (require) {

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');
    var Model = require('web.Model');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var _t = core._t;

    gui.Gui.include({
        show_screen: function(screen_name,params,refresh,skip_close_popup) {
            var screen = this.screen_instances[screen_name];
            if (!screen) {
                console.error("ERROR: show_screen("+screen_name+") : screen not found");
                return
            }
            this._super(screen_name,params,refresh,skip_close_popup);
        },
    });
})