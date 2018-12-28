odoo.define('pos_order_station.order', function(require) {
    'use strict'

    var models = require('point_of_sale.models');
    var Screen = require('point_of_sale.screens');

    models.load_fields("pos.config",['session_type']);

    Screen.ActionpadWidget.include({

        renderElement: function() {
            var self = this;
            this._super();
            if (this.pos.config.session_type == 'order') {
                self.$('.pay').hide();
                console.log('hidden render');
            }  
        }

    });
});