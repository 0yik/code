odoo.define('hilti_website_feedback.hilti_website_feedback', function (require) {
'use strict';

	var ajax = require('web.ajax');

	$(document).on('click', '.submit', function(){
		if($("#result").text() != '0'){
			ajax.jsonRpc("/store_feedback", 'call', {
				'feedback_rating': $("#result").text(),
				'feedback_description': $("#feedback_description").val(),
				'feedback_received': true,
				'id': $(".submit").data('id'),
			}).then(function(results){
				if (results){
					$('.container').html('<div class="row"><div class="col-md-12 text-center"><h3>Thank you for the feedback.</h3></div></div>')
				}
			})
		}else{
			alert('Please select the rating before submitting the response.')
		}
	})

});

$(function (){
	$('.ratingEvent').rating({ rateEnd: function (v) { $('#result').text(v); } });
});
