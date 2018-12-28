odoo.define('aikchin_modifier_fields.pos_custom', function (require) {
    "use strict";

var base = require('web_editor.base');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;
var models = require('point_of_sale.models');
var addresses = [];
//var partners = [];
var SuperPosModel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
	initialize: function(session, attributes) {
		SuperPosModel.initialize.call(this, session, attributes);
		var self = this;
		self.models.push(
		{
			model:  'res.partner',
			fields: ['name','street','city','state_id','country_id','vat','phone','fax','zip','mobile','email','barcode','write_date','property_account_position_id', 'property_payment_term_ids','delivery_address_ids', 'issuer_id'],
			domain: [['customer','=',true]],
			loaded: function(self,partners){
				self.partners = partners;
				self.db.add_partners(partners);
			}
		},
		/*{
		    model:  'hr.employee',
		    fields: ['name'],
		    loaded: function(self,issuers){
		        self.issuers = issuers;
		        self.company.issuer = null;
		        for (var i = 0; i < issuers.length; i++) {
		            if (issuers[i].id === self.company.issuer_id){
		                self.company.issuer = issuers[i];
		            }
		        }
		    },
    	},*/
		{
		    model:  'delivery.address',
		    fields: ['street','city','state_id','country_id'],
		    loaded: function(self,addresses){
		    	self.db.add_addresses(addresses);
		        self.addresses = addresses;
		        self.db.add_addresses = addresses;
		    },
    	},
    	{
		    model:  'account.payment.term',
		    fields: ['name'],
		    loaded: function(self,payments){
		        self.payments = payments;
		        self.company.payment = null;
		        for (var i = 0; i < payments.length; i++) {
		            if (payments[i].id === self.company.property_payment_term_ids){
		                self.company.payment = payments[i];
		            }
		        }
		    },
		}
		)
	},
});
});
