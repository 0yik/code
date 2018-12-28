odoo.define('modifier_ccm_pos_rental.pos_partner', function(require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var PosDB = require('point_of_sale.DB');
var QWeb = core.qweb;

models.load_fields('res.partner', ['citizenship', 'passport_no'])

// to extend search base on nric no and passport number
PosDB.include({
    _partner_search_string: function(partner){
        var str = this._super(partner);
        if(partner.citizenship == 'singaporean' && partner.nric_no) {
            str = str.split('\n');
            str += '|' + partner.nric_no + '\n';
        }
        if(partner.citizenship == 'foreigner' && partner.passport_no) {
            str = str.split('\n');
            str += '|' + partner.passport_no + '\n';
        }

        return str;
    }
});

screens.ClientListScreenWidget.include({
    // update client cached node
    saved_client_details: function(partner_id){
        var self = this;
        this.reload_partners().then(function(){
            var partner = self.pos.db.partner_by_id[partner_id];
            var partner_node = self.partner_cache.get_node(partner_id);
            if (partner_node) {
                var clientline_html = QWeb.render('ClientLine',{widget: self, partner:partner});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];
                partner_node.replaceWith(clientline);
                self.partner_cache.cache[partner_id] = clientline;
            }

            if (partner) {
                self.new_client = partner;
                self.toggle_save_button();
                self.display_client_details('show', partner);
            } else {
                self.display_client_details('hide');
            }
        });
    }
});
});
