odoo.define('forgotpwd_app_alert.forgotpwd_app_alert', function(require) {
"use strict";

var ajax = require('web.ajax');

$(document).ready(function () {

	$('.oe_reset_password_form').submit(function(e){

		var login = $('#login').val();
		var password = $('#password').val();
		var confirm_password = $('#confirm_password').val();
		var name = $('#name').val();
		var token = $('input[name="token"]').val();
		var form_submit = $('input[name="form_submit"]').val();
		
		if(login && password && confirm_password && name && token){
			if(!form_submit){
				e.preventDefault();
				ajax.jsonRpc('/check_and_update_password', 'call', {
					'login': login, 
					'password': password,
					'confirm_password': confirm_password,
					'name': name,
					'token': token,
		        }).then(function (result) {
		        	if (result['password_updated']){
		        		alert('Your password has been reset successfully. Please login to the app using the new password. Thank You.')
		        	}else{
		        		$('.oe_reset_password_form').append("<input type='hidden' name='form_submit' value='True'>");
		        		$('.oe_reset_password_form').submit();
		        	}
		        })
			}
		}
	})
    
});

});
