odoo.define('aikchin_modifier_fields.pos_db', function (require) {
    "use strict";
    
	var core = require('web.core');
	var Model = require('web.Model');
	var time = require('web.time');
	var utils = require('web.utils');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var PopupWidget = require('point_of_sale.popups');
	var DB = require('point_of_sale.DB');
	
	DB.include({
        init: function(options){
            this.add_addresses_by_id = {};
            this._super(options);
        },

        get_addresses_by_id: function(line){
            return this.add_addresses_by_id[line];
        },

        add_addresses: function(line){
        	for(var i=0 ; i < line.length; i++){
                this.add_addresses_by_id[line[i].id] = line[i];
            }
        },
    });
});
