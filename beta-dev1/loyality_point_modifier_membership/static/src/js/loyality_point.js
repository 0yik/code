odoo.define('loyality_point_modifier_membership.loyality_point_modifier_membership', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var Model = require('web.DataModel');
	var _t = core._t;
	var utils = require('web.utils');

	var QWeb = core.qweb;
	var Mutex = utils.Mutex;
	var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;
	var Backbone = window.Backbone;

	models.load_models([
	    {
	        model: 'loyalty.program',
	        condition: function(self){ return !!self.config.loyalty_id[0]; },
	        fields: ['name','pp_currency','pp_product','pp_order','rounding','membership_ids'],
	        domain: function(self){ return [['id','=',self.config.loyalty_id[0]]]; },
	        loaded: function(self,loyalties){ 
	            self.loyalty = loyalties[0]; 
	        },
	    },{
	        model: 'loyalty.rule',
	        condition: function(self){ return !!self.loyalty; },
	        fields: ['name','rule_type','product_id','category_id','cumulative','pp_product','pp_currency','spending_amount'],
	        domain: function(self){ return [['loyalty_program_id','=',self.loyalty.id]]; },
	        loaded: function(self,rules){ 

	            self.loyalty.rules = rules; 
	            self.loyalty.rules_by_product_id = {};
	            self.loyalty.rules_by_category_id = {};
	            self.loyalty.rules_by_spending_amount = {};

	            for (var i = 0; i < rules.length; i++){
	                var rule = rules[i];
	                if (rule.rule_type === 'product') {
	                    if (!self.loyalty.rules_by_product_id[rule.product_id[0]]) {
	                        self.loyalty.rules_by_product_id[rule.product_id[0]] = [rule];
	                    } else if (rule.cumulative) {
	                        self.loyalty.rules_by_product_id[rule.product_id[0]].unshift(rule);
	                    } else {
	                        self.loyalty.rules_by_product_id[rule.product_id[0]].push(rule);
	                    }
	                } else if (rule.rule_type === 'category') {
	                    var category = self.db.get_category_by_id(rule.category_id[0]);
	                    if (!self.loyalty.rules_by_category_id[category.id]) {
	                        self.loyalty.rules_by_category_id[category.id] = [rule];
	                    } else if (rule.cumulative) {
	                        self.loyalty.rules_by_category_id[category.id].unshift(rule);
	                    } else {
	                        self.loyalty.rules_by_category_id[category.id].push(rule);
	                    }
	                } else if (rule.rule_type === 'spend_amount') { 
	                	if (!self.loyalty.rules_by_spending_amount[i]) {
	                	    self.loyalty.rules_by_spending_amount[i] = [rule];
	                	} else if (rule.cumulative) {
	                	    self.loyalty.rules_by_spending_amount[i].unshift(rule);
	                	} else {
	                	    self.loyalty.rules_by_spending_amount[i].push(rule);
	                	}
	                }
	            }
	        },
	    },{
	        model: 'loyalty.reward',
	        condition: function(self){ return !!self.loyalty; },
	        fields: ['name','reward_type','minimum_points','gift_product_id','point_cost','discount_product_id','discount','point_product_id'],
	        domain: function(self){ return [['loyalty_program_id','=',self.loyalty.id]]; },
	        loaded: function(self,rewards){
	            self.loyalty.rewards = rewards; 
	            self.loyalty.rewards_by_id = {};
	            for (var i = 0; i < rewards.length;i++) {
	                self.loyalty.rewards_by_id[rewards[i].id] = rewards[i];
	            }
	        },
	    },{
	    	model: 'loyalty.membership',
	    	fields: ['name','membership_point','loyalty_program_id'],
	    	domain: function(self){ return [['loyalty_program_id','=',self.loyalty.id]]; },
	    	loaded: function(self,membership){
	    	    self.loyalty.membership = membership; 
	    	    self.loyalty.membership_by_id = {};
	    	    for (var i = 0; i < membership.length;i++) {
	    	        self.loyalty.membership_by_id[membership[i].id] = membership[i];
	    		}
	    	}

	    }
	],{'after': 'loyalty.rule'});


	var _super = models.Order;
	models.Order = models.Order.extend({

	    /* The total of points won, excluding the points spent on rewards */
	    get_won_points: function(){
	        if (!this.pos.loyalty || !this.get_client()) {
	            return 0;
	        }
	        
	        var orderLines = this.get_orderlines();
	        var rounding   = this.pos.loyalty.rounding;
	        
	        var product_sold = 0;
	        var total_sold   = 0;
	        var total_points = 0;
	        var rules  = this.pos.loyalty.rules || [];
	        var order_total = this.get_total_with_tax();

	        for (var j = 0; j < rules.length; j++) {
	            var rule = rules[j];
	            if (rule.rule_type == "spend_amount" && order_total != 0 ){
	            	total_points += round_pr((order_total / rule.spending_amount * rule.pp_currency), rounding);
	            	if (!rule.cumulative) { 
	            	    overriden = true;
	            	    break;
	            	}
	            }
	        }

	        for (var i = 0; i < orderLines.length; i++) {
	            var line = orderLines[i];
	            var product = line.get_product();
	            var rules  = this.pos.loyalty.rules_by_product_id[product.id] || [];
	            var overriden = false;

	            if (line.get_reward()) {  // Reward products are ignored
	                continue;
	            }
	            
	            for (var j = 0; j < rules.length; j++) {
	                var rule = rules[j];
	                total_points += round_pr(line.get_quantity() * rule.pp_product, rounding);
	                total_points += round_pr(line.get_price_with_tax() * rule.pp_currency, rounding);
	                // if affected by a non cumulative rule, skip the others. (non cumulative rules are put
	                // at the beginning of the list when they are loaded )
	                if (!rule.cumulative) { 
	                    overriden = true;
	                    break;
	                }
	            }

	            // Test the category rules
	            if ( product.pos_categ_id ) {
	                var category = this.pos.db.get_category_by_id(product.pos_categ_id[0]);
	                while (category && !overriden) {
	                    var rules = this.pos.loyalty.rules_by_category_id[category.id] || [];
	                    for (var j = 0; j < rules.length; j++) {
	                        var rule = rules[j];
	                        total_points += round_pr(line.get_quantity() * rule.pp_product, rounding);
	                        total_points += round_pr(line.get_price_with_tax() * rule.pp_currency, rounding);
	                        if (!rule.cumulative) {
	                            overriden = true;
	                            break;
	                        }
	                    }
	                    var _category = category;
	                    category = this.pos.db.get_category_by_id(this.pos.db.get_category_parent_id(category.id));
	                    if (_category === category) {
	                        break;
	                    }
	                }
	            }

	            if (!overriden) {
	                product_sold += line.get_quantity();
	                total_sold   += line.get_price_with_tax();
	            }
	        }

	        total_points += round_pr( total_sold * this.pos.loyalty.pp_currency, rounding );
	        total_points += round_pr( product_sold * this.pos.loyalty.pp_product, rounding );
	        total_points += round_pr( this.pos.loyalty.pp_order, rounding );

	        return total_points;
	    },
	    get_membership_points: function(){
	    	var loyalty = this.pos.loyalty;
	    	var total_points = this.get_new_total_points();
	    	var membership_lines = [];
	    	for (var j = 0; j < loyalty.membership.length; j++) {
	    	    var membership = loyalty.membership[j];
	    	    if (membership.membership_point > total_points){
	    	    	var member = {
	    	    		'name':membership.name,
	    	    		'membership_point':(membership.membership_point - total_points)
	    	    	}
	    	    	membership_lines.push(member);
	    	    }
	    	}
	    	return membership_lines;
	    },
	    export_for_printing: function(){
	        var json = _super.prototype.export_for_printing.apply(this,arguments);
	        if (this.pos.loyalty && this.get_client()) {
	            json.loyalty = {
	                rounding:     this.pos.loyalty.rounding || 1,
	                name:         this.pos.loyalty.name,
	                client:       this.get_client().name,
	                points_won  : this.get_won_points(),
	                points_spent: this.get_spent_points(),
	                points_total: this.get_new_total_points(), 
	                membership_lines: this.get_membership_points(),
	            };
	        }
	        return json;
	    },
	});

});

