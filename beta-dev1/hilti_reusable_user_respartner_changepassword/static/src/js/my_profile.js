odoo.define('hilti_reusable_user_respartner_changepassword.hilti_reusable_user_respartner_changepassword', function(require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var session = require('web.session');
var ajax = require('web.ajax');
var web_client = require('web.web_client');


var open_my_profile = function(parent, action){
	
	ajax.rpc("/web/action/load", { action_id: "hilti_reusable_user_respartner_changepassword.action_my_partner_view" }).done(function(result) {
        result.res_id = session.partner_id;
        return web_client.action_manager.do_action(result);
    });
	
	
};

var open_my_tester_profile = function(parent, action){
	
	ajax.rpc("/web/action/load", { action_id: "hilti_reusable_user_respartner_changepassword.action_my_tester_partner_view" }).done(function(result) {
        result.res_id = session.partner_id;
        return web_client.action_manager.do_action(result);
    });
	
	
};



core.action_registry.add("open_my_profile", open_my_profile);
core.action_registry.add("open_my_tester_profile", open_my_tester_profile);


})