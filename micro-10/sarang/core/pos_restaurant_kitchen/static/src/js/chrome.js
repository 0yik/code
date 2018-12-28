odoo.define('pos_restaurant_kitchen_chrome', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var floors = require('pos_restaurant.floors'); // depends function build_widgets of floors

    chrome.Chrome.include({
        build_widgets: function () {
            this._super();
            if (this.pos.config.screen_type && this.pos.config.screen_type == 'kitchen') {
                this.gui.set_startup_screen('kitchen_screen');
                this.gui.set_default_screen('kitchen_screen');
                this.$('.username').hide();
                $('.order-selector').hide();
            }
        },
    });

})
