odoo.define('modifier_ccm_pos_rental.gui', function(require) {
"use strict";

var core = require('web.core');
var gui = require('point_of_sale.gui');

gui.Gui.include({
    // disable sound for error
    play_sound: function(sound) {
        if (sound === 'error') {
            sound = '';
        }
        this._super(sound);
    },
});

});
