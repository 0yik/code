odoo.define('complex_kds.chrome', function (require) {

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
            if (this.pos.config.screen_type && this.pos.config.screen_type == 'summary') {
                this.gui.set_startup_screen('summary_screen');
                this.gui.set_default_screen('summary_screen');
                // this.gui.current_screen = 'summary_screen'
                this.$('.username').hide();
                $('.order-selector').hide();
            }
        },
    });
    chrome.OrderSelectorWidget.include({
        deleteorder_click_handler: function(event, $el) {
            var self  = this;
            var order = this.pos.get_order(); 
            if (!order) {
                return;
            } else if ( !order.is_empty() ){
                this.gui.show_popup('confirm',{
                    'title': _t('Destroy Current Order ?'),
                    'body': _t('You will lose any data associated with the current order'),
                    confirm: function(){
                        order.permantly_delete = true
                        self.pos.delete_current_order();
                    },
                });
            } else {
                order.permantly_delete = true
                this.pos.delete_current_order();
            }
        },
    });
});