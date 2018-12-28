odoo.define('pos_startscreen.models', function (require) {
    "use strict";

var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var floors = require('pos_restaurant.floors');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');

var _t = core._t;

//Update load models
models.load_models({
    model: 'restaurant.floor',
    fields: ['name','background_color','table_ids','sequence','pos_config_ids'],
    domain: function(self){ return [['pos_config_ids','in',self.config.id]]; },
    loaded: function(self,floors){
        self.floors = floors;
        self.floors_by_id = {};
        for (var i = 0; i < floors.length; i++) {
            floors[i].tables = [];
            self.floors_by_id[floors[i].id] = floors[i];
        }

        // Make sure they display in the correct order
        self.floors = self.floors.sort(function(a,b){ return a.sequence - b.sequence; });

        // Ignore floorplan features if no floor specified.
        self.config.iface_floorplan = !!self.floors.length;
    },
},{'after': 'restaurant.floor'});

var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        _super_posmodel.initialize.call(this, session, attributes);
        this.category = '';
    },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function (attributes, options) {
        var res = _super_order.initialize.apply(this, arguments);
        this.category = this.pos.category;
        return res;
    },
});

})