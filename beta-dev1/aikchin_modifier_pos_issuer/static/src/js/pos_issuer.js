odoo.define('aikchin_modifier_pos_issuer.pos_issuer', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');
var core = require('web.core');
var _t = core._t;
var utils = require('web.utils');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var round_pr = utils.round_precision;
var QWeb     = core.qweb;
var Widget = require('web.Widget');
var SuperPosModel = models.PosModel.prototype;
var Backbone = window.Backbone;
var _super = models.Order;
var DB = require('point_of_sale.DB');	

DB.include({
        init: function(options){
            this.add_issuer_by_id = {};
            this._super(options);
        },

        get_issuer_by_id: function(employees){
            return this.add_issuer_by_id[employees];
        },

        add_employees: function(employees){
        	for(var i=0 ; i < employees.length; i++){
                this.add_issuer_by_id[employees[i].id] = employees[i];
            }
        },
});

models.PosModel = models.PosModel.extend({
	initialize: function(session, attributes) {
		SuperPosModel.initialize.call(this, session, attributes);
		var self = this;
		this.set({
		   'selectedIssuer':   null,
		});
		function update_issuer() {
		    var order = self.get_order();
		    this.set('selectedIssuer', order ? order.get_issuer() : null );
		}
		
		this.get('orders').bind('add remove change', update_issuer, this);
        	this.bind('change:selectedOrder', update_issuer, this);
		self.models.push(
		{
			model:  'hr.employee',
			fields: ['name'],
			loaded: function(self,employees){
			    self.employees = employees;
			    self.db.add_employees(employees);
			},
		},
		)
		
	},
	get_issuer: function() {
		var order = this.get_order();
		if (order) {
		    return order.get_issuer();
		}
		return null;
	    },
});
models.Order = models.Order.extend({
   initialize: function(attributes,options){
	var self = this;
	this.set({issuer: null});
	_super.prototype.initialize.call(this,attributes,options);
    },
	

   init_from_JSON: function(json) {
	    var self = this;
	    if (json.issuer_id) {
		    json.issuer = this.pos.db.get_issuer_by_id(json.issuer_id);
	    }
 	    if (json.issuer)
		{
		this.set_issuer(json.issuer);
		}
	    _super.prototype.init_from_JSON.call(this, json); 
	  
   },
   set_issuer: function(issuer){
        this.assert_editable();
        this.set('issuer',issuer);
    },
    get_issuer: function(){
        return this.get('issuer');
    },
    get_issuer_name: function(){
        var issuer = this.get('issuer');
        return issuer ? issuer.name : "";
    },
	
 //  export_for_printing: function(){
   //     var self = this;
     //   var loaded=_super.prototype.export_as_JSON.call(this);
      //  loaded.issuer = this.get('issuer');
//	return loaded;
  //  },

    export_as_JSON: function() {
		var self = this;
		var loaded=_super.prototype.export_as_JSON.call(this);
		loaded.issuer_id = this.get_issuer() ? this.get_issuer().id : false
		return loaded;
	},
});

screens.ActionpadWidget.include({
   init: function(parent, options) {
	var self = this;
        this._super(parent, options);
	this.pos.bind('change:selectedIssuer', function() {
	    self.renderElement();
	});
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.set-issuer').click(function(){
	    var order = self.pos.get_order();
            self.gui.show_popup('issuerlist', {});
	    var issuer = order.get_issuer();
	    if (issuer){
		$('#employee_id').val(issuer.id);
	    }
	    
        });
	this.$('.pay').click(function(event) {
            var order = self.pos.get_order();
	    var issuer = order.get_issuer();
	    if(!issuer){
		alert("Please select Issuer.");
		self.gui.show_screen('products');
                return;
	    }
        });
    }
});
var IssuerPopupWidget = PopupWidget.extend({
	    template: 'IssuerPopupWidget',
	    init: function(parent, options){
		this._super(parent, options);
		this.old_issuer = this.pos.get_order().get_issuer();
	    },

    	    auto_back: true,
	    show: function(options){
	    	options = options || {};
	        this._super(options);
	        console.log(options);
		
    		this.renderElement(); 
	   },
	   click_confirm: function(){
		var employee = $('#employee_id').val();
		var order = this.pos.get('selectedOrder');
		
		var issuer = order.get_issuer();
		if (employee){
			order.set_issuer(order.pos.db.get_issuer_by_id(employee));
			this.gui.close_popup();

		}
		if (!employee){
			alert("Please select Issuer.");
			return;	
		}
		
	    }
});

gui.define_popup({name:'issuerlist', widget: IssuerPopupWidget});
});
