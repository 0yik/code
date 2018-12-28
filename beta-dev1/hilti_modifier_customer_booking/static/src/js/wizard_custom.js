
// $(document).on('click', '#booking_right_arrow', function(){ 
// 	if($('#step10').hasClass('color-code')){
// 	   $('#step10').removeClass('color-code');
// 	   $('#step20').addClass('color-code');
// 	   $('#step20').removeClass('wizard-color-code');
// 	   $('#step10').addClass('success-color-code');
// 	   $('#step30').addClass('wizard-color-code');
// 	   $('.one').removeClass('active');
// 	   $('.two').addClass('active');
// 	   $('.one').addClass('done');
// 	}
// });


// $(document).on('click', '#anchor_right_arrow', function(){ 
// 	if($('#step20').hasClass('color-code')){
// 	   $('#step20').removeClass('color-code');
// 	   $('#step20').addClass('success-color-code');
// 	   $('#step40').removeClass('wizard-color-code');
// 	   $('#step40').addClass('color-code');
// 	   $('.two').removeClass('active');
// 	   $('.three').addClass('active');
// 	   $('.two').addClass('done');
// 	}
// });   


$(document).on('click', '#calendar_left_arrow', function(){ 
	if($('#step40').hasClass('color-code')){
	   $('#step20').addClass('color-code');
	   $('#step20').removeClass('success-color-code');
	   $('#step40').addClass('wizard-color-code');
	   $('#step40').removeClass('color-code');
	   $('.three').removeClass('active');
	   $('.two').addClass('active');
	}
});  


$(document).on('click', '#anchor_left_arrow', function(){ 
	if($('#step20').hasClass('color-code')){
	   $('#step20').removeClass('color-code');
	   $('#step20').addClass('wizard-color-code');
	   $('#step10').removeClass('success-color-code');
	   $('#step10').addClass('color-code');
	   $('.two').removeClass('active');
	   $('.one').addClass('active');
	}
});

