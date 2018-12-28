odoo.define('hilti_modifier_customer_booking.hilti_modifier_customer_booking', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var Model = require('web.Model');
    var _t = core._t;
    var new_pr_result = 0;
    var caledar_load = false;
    var new_project_approve = 0;
    ajax.loadXML("/hilti_modifier_customer_booking/static/src/xml/hilti_booking_templates_view.xml", core.qweb);
    ajax.loadXML("/hilti_modifier_customer_booking/static/src/xml/booking_time_slot2.xml", core.qweb);
    var QWeb = core.qweb;
	$(document).ready(function() {

	    function check_attr_right_arrow(){
            if ($('select[name=customer] option:selected').val() &&
                $('#project option:selected').val() && $("input[name=sic]:checked").val() && $('#Contact').val()
                && $('#con_no').val() && $('#address').val() && $('#postal_code').val()) {
                var charReg = /^[a-zA-Z() ]+$/;
                if ($('#con_no').val().length == 8 && charReg.test($('#Contact').val())) {
                    $('#booking_right_arrow button').removeAttr('disabled');
                }else{
                    $("#booking_right_arrow button").attr("disabled", true);
                }
            }else {
                $("#booking_right_arrow button").attr("disabled", true);
            }
        }

        function check_attr_anchor_right_arrow(){
            if ($('#anchor_size option:selected').val() && $('#anchor_type option:selected').val() && $('#anhor_qty').val()
                && $("input[name='complexity']:checked").val()){
                    if ($.isNumeric($('#anhor_qty').val())) {
                        $("#anchor_right_arrow button").removeAttr('disabled');
                    }else{
                        $("#anchor_right_arrow button").attr("disabled", true);
                    }
                }else {
                    $("#anchor_right_arrow button").attr("disabled", true);
                }

            var an_counter = $('#anchor_count').val();
            for (var i = 2; i <= an_counter; i++) {
                var an_qty_1 = $('#anhor_qty_'+i+'').val();
                if ($('#anchor_type_'+i+' option:selected').val() && $('#anchor_size_'+i+' option:selected').val() &&
                    an_qty_1 && $("input[name='complexity_"+i+"']:checked").val()){
                    if ($.isNumeric(an_qty_1)) {
                        $("#anchor_right_arrow button").removeAttr('disabled');
                    }else{
                        $("#anchor_right_arrow button").attr("disabled", true);
                    }
                }
                else{
                    $("#anchor_right_arrow button").attr("disabled", true);
                }
            }
        }

//        $(document).on('change', '#anchor_size, #anchor_type, #anhor_qty, input[name="complexity"]', function () {
//        $(document).on('change', '.anchor_size, #anchor_type, .anhor_qty, input[name="complexity"]', function () {
        $(document).on('change', 'select[name="anchor_size"], select[name="anchor_type"], input[name="anhor_qty"], input[name="complexity"], .anhor_qty_class', function () {
            check_attr_anchor_right_arrow()
        });

        $(document).on('change', 'select[name=customer], #project, input[name=sic], #Contact, #con_no, #address, #postal_code', function () {
            check_attr_right_arrow()
        });

		$('.left_arrow').css('display', 'block');
		$('.booking_page').css('display', 'inherit');
		$('#anchor_portion').css('display', 'none');
		$('#calendar_portion').css('display', 'none');
		$('.book_for_sic').css('display', 'none');
		$('.field_starttime').css('display', 'none');
		$('.btn .dropdown-toggle .btn-default').focus();
		$('.sic').change(function() {
			if ($(this).attr('value')){
				$('.sic_valication_error')
                .css('display', 'none');
				var pr_id =  $('#project option:selected').val();
		    	 if (pr_id) {
	                  $('.project_valication_error')
	                      .css('display', 'none');
	              } else {
	                  $('.project_valication_error')
	                      .css('display', 'block');
	              }
		    	 var cs_id =  $('#customer option:selected').val();
		    	 if (cs_id) {
	                  $('.customer_valication_error')
	                      .css('display', 'none');
	              } else {
	                  $('.customer_valication_error')
	                      .css('display', 'block');
	              }
		        } 
			else {
	            $('.sic_valication_error')
	                .css('display', 'block');
	        }
			if ($(this).attr('value') == 'yes'){
				var pr_id =  $('#project option:selected').val();
				ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': pr_id}).then(function(results){
					if (results[1] == 1){
						new_project_approve = 1
						$('#step20').addClass('hidden');
					}
					else{
						new_project_approve = 0
						$('#step20').removeClass('hidden');
					}
					if (results[0] == 1){
						$('.book_class').css('display', 'none');
						new_pr_result = 1
//						$('.left_arrow').css('display', 'none');
						$('.booking_page').css('display', 'block');
						$('#anchor_portion').css('display', 'block');
//						$('#calendar_portion').css('display', 'block');
						$('.book_for_sic').css('display', 'block');
						$('#anchor_portion').css('display', 'none');
						$('.field_starttime').css('display', 'block');
					}
					else {
						new_pr_result = 0
						$('.book_for_sic').css('display', 'none');
						$('.field_starttime').css('display', 'none');
					}
				});
				
			}else{
			    $('#step20').removeClass('hidden');
			    $('#step20').addClass('wizard-color-code');
                $('.two').removeClass('active');
			}
			
				$('.left_arrow').css('display', 'block');
				$('.booking_page').css('display', 'inherit');
				$('#anchor_portion').css('display', 'none');
				$('#calendar_portion').css('display', 'none');
				$('.book_for_sic').css('display', 'none');
				$('.field_starttime').css('display', 'none');
            check_attr_right_arrow()

		});
		
		function isAlphaOrParen(str) {
			  return /^[a-zA-Z() ]+$/.test(str);
			  var charReg = /^[a-zA-Z() ]+$/;
              if (!charReg.test(str)) {
                  $('.email_validation_reset')
                      .css('display', 'block');
                  check_validate1 = false;
              } else {
                  $('.email_validation_reset')
                      .css('display', 'none');
              }
			}
		
		$('#project').change(function() {
			if ($("input[name=sic]:checked").val() == 'yes'){
				var pr_id =  $('#project option:selected').val();
				ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': pr_id}).then(function(results){
					if (results[0] == 1){
						$('.field_starttime').css('display', 'block');
					}
					else {
						$('.field_starttime').css('display', 'none');
					}
				});
				
			}
			var cu_id =  $('#customer option:selected').val();
		    	 if (cu_id){
	              $('.customer_valication_error')
	                  .css('display', 'none');
	          } else {
	              $('.customer_valication_error')
	                  .css('display', 'block');
	          }
			var pr_id =  $('#project option:selected').val();
		    	 if (pr_id && pr_id != 'create') {
                   $('.project_valication_error')
                       .css('display', 'none');
               } else {
                   $('.project_valication_error')
                       .css('display', 'block');
               }
            check_attr_right_arrow()
		});
		$('#customer').change(function() {
			var pr_id =  $('#customer option:selected').val();
		    	 if (pr_id){
                   $('.customer_valication_error')
                       .css('display', 'none');
               } else {
                   $('.customer_valication_error')
                       .css('display', 'block');
               }
               check_attr_right_arrow()
		});
		$('#Contact').change(function() {
			function isAlphaOrParen(str) {
			  var charReg = /^[a-zA-Z() ]+$/;
              if (!charReg.test(str)) {
                  $('.contact_name_validation')
                      .css('display', 'block');
                  check_validate1 = false;
              } else {
                  $('.contact_name_validation')
                      .css('display', 'none');
              }
			}
			if ($(this).val()) {
				isAlphaOrParen($(this).val());
				var cu_id =  $('#customer option:selected').val();
		    	 if (cu_id){
		              $('.customer_valication_error')
		                  .css('display', 'none');
		          } else {
		              $('.customer_valication_error')
		                  .css('display', 'block');
		          }
            	var pr_id =  $('#project option:selected').val();
   		    	 if (pr_id && pr_id != 'create') {
                        $('.project_valication_error')
                            .css('display', 'none');
                    } else {
                        $('.project_valication_error')
                            .css('display', 'block');
                    }
   		    	if ($("input[name=sic]:checked").val()) {
   		    		 $('.sic_valication_error')
                        .css('display', 'none');
       	             } else {
       	                 $('.sic_valication_error')
       	                     .css('display', 'block');
       	             }
                $('.contact_name_valication_error').css('display', 'none');
            }
            else {
            		$('.contact_name_valication_error').css('display', 'block');
            	}
            check_attr_right_arrow()
		});
		$('#con_no').change(function() {
			if ($(this).val()) {
				var cu_id =  $('#customer option:selected').val();
		    	 if (cu_id){
	              $('.customer_valication_error')
	                  .css('display', 'none');
		          } else {
		              $('.customer_valication_error')
		                  .css('display', 'block');
		          }
            	var pr_id =  $('#project option:selected').val();
   		    	 if (pr_id && pr_id != 'create') {
                        $('.project_valication_error')
                            .css('display', 'none');
                    } else {
                        $('.project_valication_error')
                            .css('display', 'block');
                    }
   		    	if ($("input[name=sic]:checked").val()) {
   		    		 $('.sic_valication_error')
                        .css('display', 'none');
       	             } else {
       	                 $('.sic_valication_error')
       	                     .css('display', 'block');
       	             }
   		    	 if ($('#Contact').val()) {
   		    		 $('.contact_name_valication_error')
                        .css('display', 'none');
   	             } else {
   	                 $('.contact_name_valication_error')
   	                     .css('display', 'block');
   	             }
                $('.contact_number_valication_error').css('display', 'none');
                if ($.isNumeric($(this).val())) {
                    $('.contact_number_validation').css(
                        'display', 'none');
                    if ($(this).val().length != 8) {
                        $('.contact_number_validation_digit')
                            .css('display',
                                'block');
                    } else {
                        $('.contact_number_validation_digit')
                            .css('display',
                                'none');
                    }
                } else {
                    $('.contact_number_validation').css(
                        'display', 'block');
                }
            }
            else {
            		$('.contact_number_valication_error').css('display', 'block');
            	}
            check_attr_right_arrow()
		});
		$('#address').change(function() {
			if ($(this).val()) {
				var cu_id =  $('#customer option:selected').val();
		    	 if (cu_id){
	              $('.customer_valication_error')
	                  .css('display', 'none');
		          } else {
		              $('.customer_valication_error')
		                  .css('display', 'block');
		          }
            	var pr_id =  $('#project option:selected').val();
   		    	 if (pr_id && pr_id != 'create') {
                        $('.project_valication_error')
                            .css('display', 'none');
                    } else {
                        $('.project_valication_error')
                            .css('display', 'block');
                    }
   		    	if ($("input[name=sic]:checked").val()) {
   		    		 $('.sic_valication_error')
                        .css('display', 'none');
       	             } else {
       	                 $('.sic_valication_error')
       	                     .css('display', 'block');
       	             }
   		    	 if ($('#Contact').val()) {
   		    		function isAlphaOrParen(str) {
   					  var charReg = /^[a-zA-Z() ]+$/;
   		              if (!charReg.test(str)) {
   		                  $('.contact_name_validation')
   		                      .css('display', 'block');
   		              } else {
   		                  $('.contact_name_validation')
   		                      .css('display', 'none');
   		              }
   					}
   		    		isAlphaOrParen($('#Contact').val());
   		    		 $('.contact_name_valication_error')
                        .css('display', 'none');
   	             } else {
   	                 $('.contact_name_valication_error')
   	                     .css('display', 'block');
   	             }
   		    	 if ($('#con_no').val()) {
   		    		 $('.contact_number_valication_error')
                        .css('display', 'none');
   		    		if ($.isNumeric($('#con_no').val())) {
   	                    $('.contact_number_validation').css(
   	                        'display', 'none');
   	                    if ($('#con_no').val().length != 8) {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'block');
   	                    } else {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'none');
   	                    }
   	                } else {
   	                    $('.contact_number_validation').css(
   	                        'display', 'block');
   	                }
   	             } else {
   	                 $('.contact_number_valication_error')
   	                     .css('display', 'block');
   	             }
                $('.address_valication_error').css('display', 'none');
            }
            else {
            		$('.address_valication_error').css('display', 'block');
            	}
            check_attr_right_arrow()
		});
		
		$('#anchor_size').change(function(){
			 if ($('#anchor_size option:selected').val()){
	    		 $('.anchor_size_valication_error')
                 .css('display', 'none');
             } else {
                 $('.anchor_size_valication_error')
                     .css('display', 'block');
             }
		});
		$('#anhor_qty').change(function(){
			var an_qty = $('#anhor_qty').val();
		   	 if (an_qty){
		   		 if ($.isNumeric(an_qty)) {
		   			 $('.qty_number_validation')
		                .css('display', 'none');
		   		 }
		   		 else{
		   			 $('.qty_number_validation')
		                .css('display', 'block');
		   			 check_validate = true;
		   		 }
		   		 $('.ancor_qty_valication_error')
		            .css('display', 'none');
		        } else {
		            $('.ancor_qty_valication_error')
		                .css('display', 'block');
		        }
		});
		
		
		$(".image_redio_button").click(function(){
	   		 $('.site_condition_valication_error')
	            .css('display', 'none');
		});
		$('#anchor_type').change(function(){
			if ($('#anchor_type option:selected').val()){
	    		 $('.anchor_type_valication_error')
                .css('display', 'none');
            } else {
                $('.anchor_type_valication_error')
                    .css('display', 'block');
            }
		});
		$('#postal_code').change(function() {
			if ($(this).val()) {
				var cu_id =  $('#customer option:selected').val();
		    	 if (cu_id){
	              $('.customer_valication_error')
	                  .css('display', 'none');
		          } else {
		              $('.customer_valication_error')
		                  .css('display', 'block');
		          }
            	var pr_id =  $('#project option:selected').val();
		    	 if (pr_id && pr_id != 'create') {
                    $('.project_valication_error')
                        .css('display', 'none');
                } else {
                    $('.project_valication_error')
                        .css('display', 'block');
                }
   		    	if ($("input[name=sic]:checked").val()) {
		    		 $('.sic_valication_error')
                    .css('display', 'none');
   	             } else {
   	                 $('.sic_valication_error')
   	                     .css('display', 'block');
   	             }
		    	 if ($('#Contact').val()) {
		    		 function isAlphaOrParen(str) {
	   					  var charReg = /^[a-zA-Z() ]+$/;
	   		              if (!charReg.test(str)) {
	   		                  $('.contact_name_validation')
	   		                      .css('display', 'block');
	   		              } else {
	   		                  $('.contact_name_validation')
	   		                      .css('display', 'none');
	   		              }
	   					}
	   		    		isAlphaOrParen($('#Contact').val());
		    		 $('.contact_name_valication_error')
                    .css('display', 'none');
	             } else {
	                 $('.contact_name_valication_error')
	                     .css('display', 'block');
	             }
		    	 if ($('#con_no').val()) {
   		    		 $('.contact_number_valication_error')
                        .css('display', 'none');
   		    		if ($.isNumeric($('#con_no').val())) {
   	                    $('.contact_number_validation').css(
   	                        'display', 'none');
   	                    if ($('#con_no').val().length != 8) {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'block');
   	                    } else {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'none');
   	                    }
   	                } else {
   	                    $('.contact_number_validation').css(
   	                        'display', 'block');
   	                }
   	             } else {
   	                 $('.contact_number_valication_error')
   	                     .css('display', 'block');
   	             }
		    	 if ($('#address').val()) {
		    		 $('.address_valication_error')
                    .css('display', 'none');
	             } else {
	                 $('.address_valication_error')
	                     .css('display', 'block');
	             }
                $('.postal_code_valication_error').css('display', 'none');
            }
            else {
            		$('.postal_code_valication_error').css('display', 'block');
            	}
            check_attr_right_arrow()
		});

		$(document).ready(function (e) {
		     $("#booking_right_arrow").click(function (e) {
		    	 var check_validate = false;
		    	 var pr_id =  $('#project option:selected').val();
		    	 if (pr_id && pr_id != 'create') {
                     $('.project_valication_error')
                         .css('display', 'none');
                 } else {
                     $('.project_valication_error')
                         .css('display', 'block');
                     check_validate = true;
                 }
                 var cust_id =  $('#customer option:selected').val();
                 if (!cust_id){
		             $('.customer_valication_error')
		                 .css('display', 'block');
		             check_validate = true;
			     }
                 else{
                	 $('.customer_valication_error')
	                 .css('display', 'none');
                 }
		    	 if ($("input[name=sic]:checked").val()) {
		    		 $('.sic_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.sic_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 if ($('#Contact').val()) {
		    		 function isAlphaOrParen(str) {
	   					  var charReg = /^[a-zA-Z() ]+$/;
	   		              if (!charReg.test(str)) {
	   		                  $('.contact_name_validation')
	   		                      .css('display', 'block');
	   		               check_validate = true;
	   		              } else {
	   		                  $('.contact_name_validation')
	   		                      .css('display', 'none');
	   		              }
	   					}
	   		    		isAlphaOrParen($('#Contact').val());
		    		 $('.contact_name_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.contact_name_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 if ($('#con_no').val()) {
		    		 $('.contact_number_valication_error')
                     .css('display', 'none');
		    		 if ($.isNumeric($('#con_no').val())) {
   	                    $('.contact_number_validation').css(
   	                        'display', 'none');
   	                    if ($('#con_no').val().length != 8) {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'block');
   	                     check_validate = true;
   	                    } else {
   	                        $('.contact_number_validation_digit')
   	                            .css('display',
   	                                'none');
   	                    }
   	                } else {
   	                    $('.contact_number_validation').css(
   	                        'display', 'block');
   	                 check_validate = true;
   	                }
	             } else {
	                 $('.contact_number_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 if ($('#address').val()) {
		    		 $('.address_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.address_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 if ($('#postal_code').val()) {
		    		 $('.postal_code_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.postal_code_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 if (check_validate == false){
		    	        if ($("input[name=sic]:checked").val() == 'yes'){
                        	if (caledar_load == false){
	   					    	 setTimeout(function(){ 
	   					    		 $('.fc-next-button').click();
	   					    		 caledar_load= true;
	   					    	 }, 500);
  				    	 	}

                            var pr_id =  $('#project option:selected').val();
                            ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': pr_id}).then(function(results){
                                if (results[0] == 1){
                                    $("#booking_portion").animate({width:'toggle'},100 );
                                    $("#calendar_portion").animate({width:'toggle'},100);
//                                    $('.th').removeClass('done');
                                    $('.three').addClass('active');
                                    $('#step40').removeClass('wizard-color-code');
                                    $('#step40').addClass('color-code');
                                }else{
                                    $("#booking_portion").animate({width:'toggle'},100 );
                                    $("#anchor_portion").animate({width:'toggle'},100);
                                }
                            });
                        }else{
                            $("#booking_portion").animate({width:'toggle'},100 );
                            $("#anchor_portion").animate({width:'toggle'},100);
                        }
//		    		 $("#booking_portion").animate({width:'toggle'},100 );
//			    	 $("#anchor_portion").animate({width:'toggle'},100);
             if($('#step10').hasClass('color-code')){
               $('#step10').removeClass('color-code');
               $('#step20').addClass('color-code');
               $('#step20').removeClass('wizard-color-code');
               $('#step10').addClass('success-color-code');
               $('#step30').addClass('wizard-color-code');
               $('.one').removeClass('active');
               $('.two').addClass('active');
               $('.one').addClass('done');
               $('.first').removeClass('first-done');
              }
		    	 }
		     });
		     $("#anchor_left_arrow").click(function (e) {
		    	 $("#anchor_portion").animate({width:'toggle'},100);
		         $("#booking_portion").animate({width:'toggle'},100 );        
		     });
		     
		     $("#anchor_right_arrow").click(function (e) {
		    	 var check_validate = false;
		    	 if ($('#anchor_size option:selected').val()){
		    		 $('.anchor_size_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.anchor_size_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 
		    	 if ($('#anchor_type option:selected').val()){
		    		 $('.anchor_type_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.anchor_type_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 var an_qty = $('#anhor_qty').val();
		    	 if (an_qty){
		    		 if ($.isNumeric(an_qty)) {
		    			 $('.qty_number_validation')
	                     .css('display', 'none');
		    		 }
		    		 else{
		    			 $('.qty_number_validation')
	                     .css('display', 'block');
		    			 check_validate = true;
		    		 }
		    		 $('.ancor_qty_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.ancor_qty_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
				 var radioValue = $("input[name='complexity']:checked").val();
		    	 if (radioValue) {
		    		 $('.site_condition_valication_error')
                     .css('display', 'none');
	             } else {
	                 $('.site_condition_valication_error')
	                     .css('display', 'block');
	                 check_validate = true;
	             }
		    	 var an_counter = $('#anchor_count').val();
		    	 for (var i = 2; i <= an_counter; i++) {
						if ($('#anchor_type_'+i+' option:selected').val()){
							$('.anchor_type_valication_error_'+i)
		                     .css('display', 'none');
						}
						else{
							$('.anchor_type_valication_error_'+i)
		                     .css('display', 'block');
							check_validate = true;
						}
						if ($('#anchor_size_'+i+' option:selected').val()){
							$('.anchor_size_valication_error_'+i)
		                     .css('display', 'none');
						}
						else{
							$('.anchor_size_valication_error_'+i)
		                     .css('display', 'block');
							check_validate = true;
						}
						var an_qty_1 = $('#anhor_qty_'+i+'').val();
						if (an_qty_1){
							if ($.isNumeric(an_qty_1)) {
				    			 $('.qty_number_validation_'+i)
			                     .css('display', 'none');
				    		 }
				    		 else{
				    			 $('.qty_number_validation_'+i)
			                     .css('display', 'block');
				    			 check_validate = true;
				    		 }
				    		 $('.ancor_qty_valication_error_'+i)
		                     .css('display', 'none');
			             } else {
			                 $('.ancor_qty_valication_error_'+i)
			                     .css('display', 'block');
			                 check_validate = true;
			             }
						var radioValue = $("input[name='complexity_"+i+"']:checked").val();
						if (radioValue) {
				    		 $('.site_condition_valication_error_'+i)
		                     .css('display', 'none');
			             } else {
			                 $('.site_condition_valication_error_'+i)
			                     .css('display', 'block');
			                 check_validate = true;
			             }
					}
		    	 if (check_validate == false){
			    	 $("#anchor_portion").animate({width:'toggle'},100);
			    	 if (caledar_load == false){
				    	 setTimeout(function(){ 
				    		 $('.fc-next-button').click();
				    		 caledar_load= true;
				    	 }, 500);
			    	 }
			    	 $('.book_class').css('display', 'block');
			    	 $("#calendar_portion").animate({width:'toggle'},100);
             if($('#step20').hasClass('color-code')){
               $('#step20').removeClass('color-code');
               $('#step20').addClass('success-color-code');
               $('#step40').removeClass('wizard-color-code');
               $('#step40').addClass('color-code');
               $('.two').removeClass('active');
               $('.three').addClass('active');
               $('.two').addClass('done');
               $('.first').addClass('first-done');
            }
		    	 }
		     });
		     $("#calendar_left_arrow").click(function(e){
		        if ($("input[name=sic]:checked").val() == 'yes'){
                    var pr_id =  $('#project option:selected').val();
                    ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': pr_id}).then(function(results){
                        if (results[0] == 1){
                            $("#calendar_portion").animate({width:'toggle'},100);
                            $("#booking_portion").animate({width:'toggle'},100 );
                            $('.one').removeClass('done');
                            $('.one').addClass('active');
                            $('.first').removeClass('success-color-code');
                            $('.first').addClass('color-code');
                        }else{
                            $("#calendar_portion").animate({width:'toggle'},100);
                            $("#anchor_portion").animate({width:'toggle'},100 );
                        }
                    });
                }else{
                    $("#calendar_portion").animate({width:'toggle'},100);
                    $("#anchor_portion").animate({width:'toggle'},100 );
                }
//		    	 $("#calendar_portion").animate({width:'toggle'},100);
//		    	 $("#anchor_portion").animate({width:'toggle'},100 );
		    	 $('.first').removeClass('first-done');
		     });
		 });
		
		$("#append").click( function(e) {
	        e.preventDefault(); 
	        var masters_result = [];
	        var masters_size_result = [];
	        $('a.remove_this').remove();
	        var an_counter = $('#anchor_count').val();
	        $("#anchor_count").val(parseInt(an_counter) + 1)
	        var an_counter1 = $('#anchor_count').val();
	    	ajax.jsonRpc("/masters", 'call', {}).then(function(results){
	    		masters_result = results[0];
	    		masters_size_result = results[1];
	    	}).then(function(results){
		        $(".inc").append(QWeb.render('anchor_snippet', {
	                'master_ids': masters_result, 
	                'master_size_ids': masters_size_result,
	                'count': an_counter1,
	            }));;
	    	});
	    	
		    jQuery(document).on('click', '.remove_this', function() {
		        jQuery(this).parent('.anchor_main').remove();
		    });
		    check_attr_anchor_right_arrow()
		});
		
		
		$('.normal_checkbox').change(function() {
		    if (this.checked) {
		        // the checkbox is now checked 
		    	$(".normal_submit_bottom").removeAttr('disabled');
		    } else {
		        // the checkbox is now no longer checked
		    	$(".normal_submit_bottom").attr("disabled", "disabled")
		    }
		});
		
		$('.sic_checkbox').change(function() {
		    if (this.checked) {
		        // the checkbox is now checked 
		    	$(".sic_submit_bottom").removeAttr('disabled');
		    } else {
		        // the checkbox is now no longer checked
		    	$(".sic_submit_bottom").attr("disabled", "disabled")
		    }
		});
		
		$('.special_checkbox').change(function() {
		    if (this.checked) {
		        // the checkbox is now checked 
		    	$(".special_submit_bottom").removeAttr('disabled');
		    } else {
		        // the checkbox is now no longer checked
		    	$(".special_submit_bottom").attr("disabled", "disabled")
		    }
		});
		
		/*jQuery(document).on('click', '.normal_submit_bottom', function() {
			$(".normal_submit_bottom").attr("disabled", "disabled")
		});
		jQuery(document).on('click', '.special_submit_bottom', function() {
			$(".special_submit_bottom").attr("disabled", "disabled")
		});
		jQuery(document).on('click', '.sic_submit_bottom', function() {
			$(".sic_submit_bottom").attr("disabled", "disabled")
		});*/
		
		jQuery(document).on('click', '.selection-color-content', function() {
			var $this = $(this);
            if ($this.val())
                $this.addClass('used');
            else
                $this.removeClass('used');
		});
		jQuery(document).on('blur', '.anhor_qty_class', function() {
			var $this = $(this);
            if ($this.val())
                $this.addClass('used');
            else
                $this.removeClass('used');
		});
		
		jQuery(document).on('change', '.anhor_qty_class', function() {
			var item = $(this).val();
    		var co = $(this).attr('index');
    		if (item){
				if ($.isNumeric(item)) {
	    			 $('.qty_number_validation_'+String(co))
                     .css('display', 'none');
	    		 }
	    		 else{
	    			 $('.qty_number_validation_'+String(co))
                     .css('display', 'block');
	    		 }
	    		 $('.ancor_qty_valication_error_'+String(co))
                 .css('display', 'none');
             } else {
                 $('.ancor_qty_valication_error_'+String(co))
                     .css('display', 'block');
             }
		});
		
		jQuery(document).on('change', '.js_anchor_size_auto', function() {
    		var item = $(this).val();
    		var co = $(this).attr('index');
    		if (item){
    			$('.anchor_size_valication_error_'+String(co))
                .css('display', 'none');
    		}
    		else{
    			$('.anchor_size_valication_error_'+String(co))
                .css('display', 'block');
    		}
		});
		
		jQuery(document).on('click', '.image_redio_button', function() {
    		var co = $(this).attr('index');
    		if (co){
	    		var radioValue = $("input[name='complexity_"+String(co)+"']:checked").val();
				if (radioValue) {
		    		 $('.site_condition_valication_error_'+String(co))
	                 .css('display', 'none');
	             } else {
	                 $('.site_condition_valication_error_'+String(co))
	                     .css('display', 'block');
	             }

    		}
    		check_attr_anchor_right_arrow()
		});
		
		jQuery(document).on('change', '.js_anchor_type_auto', function() {
    		var item = $(this).val();
    		var co = $(this).attr('index');
    		
    		if (item){
				$('.anchor_type_valication_error_'+String(co))
                 .css('display', 'none');
    			$("#anchor_size_"+String(co)+" option:not([value=''])").remove();
		    	$('#small_'+String(co) +'> img').remove();
		    	$('#medium_'+String(co) +'> img').remove();
		    	$('#complex_'+String(co) +'> img').remove();
		    	ajax.jsonRpc("/get_anchor_size", 'call', {'selected_id': item}).then(function(anchor_size){
		    		_.each(anchor_size[0], function(size) {
		    			$('#anchor_size_'+String(co)).children("option").eq(0).after('<option value="'+size.id+'">'+size.name+'</option> ');
		    		});
		    		$('#small_'+String(co)+' #simple').attr('data', anchor_size[4]);
		    		$('#medium_'+String(co)+' #medium').attr('data', anchor_size[5]);
		    		$('#complex_'+String(co)+' #complex').attr('data', anchor_size[6]);
		    		$('#small_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[1]+'" class="img-responsive img-radio added_images" />');
		    		$('#medium_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[2]+'" class="img-responsive img-radio added_images" />');
		    		$('#complex_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[3]+'" class="img-responsive img-radio added_images" />');
		    	});
		    	$('#display_none_sitecondition_'+String(co)).css('display', 'block');
		    }
		    else{
		    	$('.anchor_type_valication_error_'+String(co))
                .css('display', 'block');
		    	$('#display_none_sitecondition_'+String(co)).css('display', 'none');
		    	$("#anchor_size_"+String(co)+" option:not([value=''])").remove();
		    }
    		$(".image_redio_button").click(function(){
    	    	$(this).find('input.img_redio').prop("checked", true);
    	    	$(this).parent().find('img.border_redio_image').removeClass('border_redio_image');
    	    	$(this).find('img.added_images').addClass('border_redio_image')
    	    });
    	});

	    jQuery(document).on('click', '.remove_this', function() {
                var an_counter = $('#anchor_count').val();
                $("#anchor_count").val(parseInt(an_counter) - 1)
                $("#anchor_"+String(parseInt($('#anchor_count').val()))).children().eq(0).before('<a class="remove_this fa fa-remove" style="color: #d2051e;cursor: pointer;margin-left: 67%;">Remove</a>');
                jQuery(this).parent('.anchor_main').remove();
                check_attr_anchor_right_arrow()
	    });
	    
	    $(".image_redio_button").click(function(){
	    	$(this).find('input.img_redio').prop("checked", true);
	    	$(this).parent().find('img.border_redio_image').removeClass('border_redio_image');
	    	$(this).find('img.added_images').addClass('border_redio_image')
	    });
		
		$('#project').change(function(){
		    var item = $(this).val();
		    
		    if (item === "more"){
		    	ajax.jsonRpc("/booking_all", 'call', {}).then(function(bookings){
		    		_.each(bookings, function(booking) {
		    			$('#project').children("option").eq(6).before('<option value="'+booking.id+'">'+booking.name+'</option> ');
		    		});
		    	});
		    	$('#more_project').remove();
		    }
		    if (item){
		    	ajax.jsonRpc("/get_project_address", 'call', {'project_id': item}).then(function(address){
		    		if (address && address[0] && address[1]){
		    			$('#address').val(address[0])
		    			$('#postal_code').val(address[1])
		    			$('.address_valication_error')
	                     .css('display', 'none');
		    			$('.postal_code_valication_error')
	                     .css('display', 'none');
	                     check_attr_right_arrow()
		    		}
		    		else{
		    			$('#address').val('')
		    			$('#postal_code').val('')
		    		}
		    	});
		    	if ($("input[name=sic]:checked").val() == 'yes'){
		    		ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': item}).then(function(results){
		    			if (results[1] == 1){
							new_project_approve = 1
						}
						else{
							new_project_approve = 0
						}
		    			if (results[0] == 1){
		    				new_pr_result = 1
//		    				$('.left_arrow').css('display', 'none');
		    				$('.booking_page').css('display', 'block');
		    				$('#anchor_portion').css('display', 'block');
//		    				$('#calendar_portion').css('display', 'block');
		    				$('.book_for_sic').css('display', 'block');
		    				$('#anchor_portion').css('display', 'none');
		    				$('#step20').addClass('hidden');
		    			}
		    			else {
		    				new_pr_result = 0
		    				$('.book_for_sic').css('display', 'none');
		    				$('#step20').removeClass('hidden');
		    			}
		    		});
		    		
		    	}else{
		    	    $('#step20').removeClass('hidden');
		    	}
		    	
		    		$('.left_arrow').css('display', 'block');
		    		$('.booking_page').css('display', 'inherit');
		    		$('#anchor_portion').css('display', 'none');
		    		$('#calendar_portion').css('display', 'none');
		    		$('.book_for_sic').css('display', 'none');
		    	
		    	
		    }
		    if (item === "create"){
		    	$('#myModal').modal('show');		    	
		    }
		});
		
		$('#anchor_type').change(function(){
		    var item = $(this).val();
		    
		    if (item){
		    	$("#anchor_size option:not([value=''])").remove();
		    	$('.small > img').remove();
		    	$('.medium > img').remove();
		    	$('.complex > img').remove();
		    	ajax.jsonRpc("/get_anchor_size", 'call', {'selected_id': item}).then(function(anchor_size){
		    		_.each(anchor_size[0], function(size) {
		    			$('#anchor_size').children("option").eq(0).after('<option value="'+size.id+'">'+size.name+'</option> ');
		    		});
		    		$('.small #simple').attr('data', anchor_size[4]);
		    		$('.medium #medium').attr('data', anchor_size[5]);
		    		$('.complex #complex').attr('data', anchor_size[6]);
		    		$('.small').prepend('<img src="data:image/png;base64,'+anchor_size[1]+'" class="img-responsive img-radio added_images" />');
		    		$('.medium').prepend('<img src="data:image/png;base64,'+anchor_size[2]+'" class="img-responsive img-radio added_images" />');
		    		$('.complex').prepend('<img src="data:image/png;base64,'+anchor_size[3]+'" class="img-responsive img-radio added_images" />');
		    	});
		    	$('.display_none_sitecondition').css('display', 'block');
		    }
		    else{
		    	$('.display_none_sitecondition').css('display', 'none');
		    	$("#anchor_size option:not([value=''])").remove();
		    }

		});
		
		$("input#create_project").click(function(){
			setTimeout(function(){
				$('#myModal').modal('hide');
				$('#project_name').val('');
			}, 5000);
			
		});
		
		
		$(".button_book_sic").click(function(){
			var check_validate = false;
			var cu_id =  $('#customer option:selected').val();
	    	 if (cu_id){
             $('.customer_valication_error')
                 .css('display', 'none');
	          } else {
	              $('.customer_valication_error')
	                  .css('display', 'block');
	              check_validate = true;
	          }
	    	 var pr_id =  $('#project option:selected').val();
	    	 if (pr_id && pr_id != 'create') {
                $('.project_valication_error')
                    .css('display', 'none');
            } else {
                $('.project_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
	    	 if ($("input[name=sic]:checked").val()) {
	    		 $('.sic_valication_error')
                .css('display', 'none');
            } else {
                $('.sic_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
//	    	 if ($('#re_time_sic').val()) {
	    	   if ($('#re_time_sic_hours').val() && $('#re_time_sic_minutes').val()) {
	    		 $('.re_time_sic_error')
	                .css('display', 'none');
	    	 }else{
	    		 $('.re_time_sic_error')
                 .css('display', 'block');
             check_validate = true;
	    	 }
	    	 if ($('#Contact').val()) {
	    		 function isAlphaOrParen(str) {
  					  var charReg = /^[a-zA-Z() ]+$/;
  		              if (!charReg.test(str)) {
  		                  $('.contact_name_validation')
  		                      .css('display', 'block');
  		               check_validate = true;
  		              } else {
  		                  $('.contact_name_validation')
  		                      .css('display', 'none');
  		              }
  					}
  		    		isAlphaOrParen($('#Contact').val());
	    		 $('.contact_name_valication_error')
                .css('display', 'none');
            } else {
                $('.contact_name_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
	    	 if ($('#con_no').val()) {
	    		 $('.contact_number_valication_error')
                .css('display', 'none');
	    		 if ($.isNumeric($('#con_no').val())) {
	                    $('.contact_number_validation').css(
	                        'display', 'none');
	                    if ($('#con_no').val().length != 8) {
	                        $('.contact_number_validation_digit')
	                            .css('display',
	                                'block');
	                     check_validate = true;
	                    } else {
	                        $('.contact_number_validation_digit')
	                            .css('display',
	                                'none');
	                    }
	                } else {
	                    $('.contact_number_validation').css(
	                        'display', 'block');
	                 check_validate = true;
	                }
            } else {
                $('.contact_number_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
	    	 if ($('#address').val()) {
	    		 $('.address_valication_error')
                .css('display', 'none');
            } else {
                $('.address_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
	    	 if ($('#postal_code').val()) {
	    		 $('.postal_code_valication_error')
                .css('display', 'none');
            } else {
                $('.postal_code_valication_error')
                    .css('display', 'block');
                check_validate = true;
            }
	    	 
			if (check_validate == false){
				setTimeout(function(){
					ajax.jsonRpc("/user_book_slot", 'call', {}).then(function(results){
						var open_popup = false;
						if (results[0].start == false || results[0].end == false || results[0].start_time == false || results[0].end_time == false || results[0].Booking_date == false){
							open_popup = true;
						}
						console.log('-----------ssss--------------');
						
						if (results[0].start >= 12){
							var start = results[0].start_time + " " + 'PM'
						}
						else{
							var start = results[0].start_time + " " + 'AM'
						}
						if (results[0].end >= 12){
							var end = results[0].end_time + " " + 'PM'
						}
						else{
							var end = results[0].end_time + " " + 'AM'
						}
						if (results[0].start && results[0].end){
							var final_start_end = start + " - " + end
						}
						else{
							var final_start_end = ''
						}
						if ($('#customer option:selected').val()){
							var cust_name = $('#customer option:selected').text();
						}
						else{
							var cust_name = $('#customer option:selected').val();
						}
						if ($('#project option:selected').val()){
							var pr_name = $('#project option:selected').text();
						}
						else{
							var pr_name = $('#project option:selected').val();
						}
						if ($("input[name=sic]:checked").val() == 'yes'){
							var sic = "Yes"
						}
						if ($("input[name=sic]:checked").val() == 'no'){
							var sic = "No"
						}
						if (open_popup == false){
							$('.select_calendar_error')
		                    .css('display', 'none');
							$('#booking_confirmation_sic').modal('show');
							$('#booking_point_sic').html(QWeb.render('booking_picker_div', {
								'cust_name': cust_name,
								'pr_name': pr_name,
								'cust_id': $('#customer option:selected').val(),
								'pr_id': $('#project option:selected').val(),
								'co_name': $('#Contact').val(),
								'co_no': $('#con_no').val(),
								'sic': sic,
								'booking_type': 'sic_booking',
//								'requested_time': $('#re_time_sic').val(),
								'requested_time': $('#re_time_sic_hours').val() +':'+  $('#re_time_sic_minutes').val(),
								'b_date': results[0].Booking_date,
								'tester_name': results[0].tester_name,
								'tester_phone': results[0].tester_contact,
								'b_time': final_start_end,
								'new_pr_result': new_pr_result,
								'tm_id': results[0].time_slot_booking,
								'address': $('#address').val(),
								'postal_code': $('#postal_code').val(),
								'created_anchor': false,
					        }))
						}
						else{
							$('.select_calendar_error')
		                    .css('display', 'block');
						}
					});
					}, 500);
				/*$('#booking_sic_request').modal('show');*/
			}
		});

		$(".remove_address").click(function(){
		    $('#address').val('');
		    $('#postal_code').val('');

                var longitude = 103.83050972046;
                var latitude = 1.304787132947;
                var address = "Default location is HILTI Office"
                var opts = {
                    zoom: 11,
                    center: new GeoPoint(longitude, latitude),
//                    center: new GeoPoint(103.83050972046, 1.304787132947),
                    enableDefaultLogo: false,
                    showCopyright: false
                };
                map = new SD.genmap.Map(document.getElementById('map'), opts);

                var icon = new SD.genmap.MarkerImage({
                    image : "/hilti_modifier_customer_booking/static/src/img/openrice_icon.png",
                    title : address,
                    iconSize : new Size(16, 24),
                    iconAnchor : new Point(7, 15),
                    infoWindowAnchor : new Point(5, 0)
                });

                mm = new SD.genmap.MarkerStaticManager({map:map});

                if (latitude && longitude){
                    var geo = new GeoPoint(parseFloat(longitude), parseFloat(latitude));
                    var marker = mm.add({
                        position: geo,
                        map: map,
                        icon: icon
                    });
                    map.setCenter(marker.position, map.zoom);
                }

		});

		$(".button_date_special").click(function(){
			//$('.button_date_special').attr("data-dismiss", "model");
			var special_not_goen = false;
			var all_anchor = [];
			var created_anchor = [];
			var total_hours = [];
			var an_counter = $('#anchor_count').val();
			if ($('#anchor_size option:selected').val()){
				var an_size = $('#anchor_size option:selected').val();
			}
			else{
				var an_size = $('#anchor_size option:selected').val();
			}
			if ($('#anchor_type option:selected').val()){
				var an_type = $('#anchor_type option:selected').val();
			}
			else{
				var an_type = $('#anchor_type option:selected').val();
			}
			var an_qty = $('#anhor_qty').val()
			var radioValue = $("input[name='complexity']:checked").val();
			var radioValue_integer = $("input[name='complexity']:checked").attr('data');
			total_hours.push(String(parseFloat(radioValue_integer) * parseFloat(an_qty)))
			all_anchor.push([String(an_size),String(an_type)])
			ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size, 'an_type': an_type, 'an_qty': an_qty, 'redio_val': radioValue, 'an_name': 1}).then(function(results){
				created_anchor.push(parseInt(results))
			});
			for (var i = 2; i <= an_counter; i++) {
				var radioValue_integer1 = $("input[name='complexity_"+i+"']:checked").attr('data');
				var an_qty_1 = $('#anhor_qty_'+i+'').val()
				total_hours.push(String(parseFloat(radioValue_integer1) * parseFloat(an_qty_1)))
				if ($('#anchor_type_'+i+' option:selected').val()){
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				else{
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				if ($('#anchor_size_'+i+' option:selected').val()){
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				else{
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				all_anchor.push([String(an_size_1),String(an_type_1)])
				var radioValue = $("input[name='complexity_"+i+"']:checked").val();
				ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size_1, 'an_type': an_type_1, 'an_qty': an_qty_1, 'redio_val': radioValue, 'an_name': i}).then(function(results){
					created_anchor.push(parseInt(results))
				});
			}
			var sic = false;
			if ($('#project option:selected').val()){
				var pr_name = $('#project option:selected').text();
			}
			else{
				var pr_name = $('#project option:selected').val();
			}
			if ($("input[name=sic]:checked").val() == 'yes'){
				sic = "Yes"
			}
			if ($("input[name=sic]:checked").val() == 'no'){
				sic = "No"
			}
			if ($('#customer option:selected').val()){
				var cust_name = $('#customer option:selected').text();
			}
			else{
				var cust_name = $('#customer option:selected').val();
			}
			if ($('#st_time').val()){
				$('.special_start_time_error')
                .css('display', 'none');
				var time = $('#st_time').val();
				var hours = Number(time.match(/^(\d+)/)[1]);
				var minutes = Number(time.match(/:(\d+)/)[1]);
				var AMPM = time.match(/\s(.*)$/)[1].toLowerCase();

				if (AMPM == "pm" && hours < 12) hours = hours + 12;
				if (AMPM == "am" && hours == 12) hours = hours - 12;
				var sHours = hours.toString();
				var sMinutes = minutes.toString();
				if (hours < 10) sHours = "0" + sHours;
				if (minutes < 10) sMinutes = "0" + sMinutes;
				var st_time = sHours +':'+sMinutes
				if ($('#start_date').val()) {
					$('.special_start_date_error')
	                .css('display', 'none');
					var backend_st_dt = $('#start_date').val() + ' ' + st_time + ':' + '00'
				}
				else{
					$('.special_start_date_error')
	                .css('display', 'block');
					special_not_goen = true;
				}
			}
			else {
				special_not_goen = true;
				$('.special_start_time_error')
                .css('display', 'block');
				var st_time = ''
					var backend_st_dt = $('#start_date').val() + ' ' + '00:00' + ':' + '00'
			}
			if ($('#ed_time').val()){
				$('.special_end_time_error')
                .css('display', 'none');
				var time = $('#ed_time').val();
				var hours = Number(time.match(/^(\d+)/)[1]);
				var minutes = Number(time.match(/:(\d+)/)[1]);
				var AMPM = time.match(/\s(.*)$/)[1].toLowerCase();

				if (AMPM == "pm" && hours < 12) hours = hours + 12;
				if (AMPM == "am" && hours == 12) hours = hours - 12;
				var sHours = hours.toString();
				var sMinutes = minutes.toString();
				if (hours < 10) sHours = "0" + sHours;
				if (minutes < 10) sMinutes = "0" + sMinutes;
				var en_time = sHours +':'+sMinutes
				if ($('#end_date').val()){
					$('.special_end_date_error')
	                .css('display', 'none');
					var backend_ed_dt = $('#end_date').val() + ' ' + en_time + ':' + '00'
				}
				else{
					$('.special_end_date_error')
	                .css('display', 'block');
					special_not_goen = true;
				}
			}
			else {
				$('.special_end_time_error')
                .css('display', 'block');
				special_not_goen = true;
				var en_time = ''
				var backend_ed_dt = $('#end_date').val() + ' ' + '00:00' + ':' + '00'
			}
			
			var check_tester_free = false;
			
			if ($("input[name=sic]:checked").val() == 'yes'){
	    		ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': $('#project option:selected').val()}).then(function(results){
	    			if (results[0] == 1){
	    				all_anchor = ['sic_booking']
	    				total_hours = []
					}
	    		});
			}
			
			if (special_not_goen == false){
			setTimeout(function(){
			ajax.jsonRpc("/dedicated_support_tester", 'call', {'start_time': st_time,
				'start_date': $('#start_date').val(), 'end_time': en_time, 'end_date': $('#end_date').val(),'total_hours': total_hours,
				'all_anchors': all_anchor, 'project_id': $('#project option:selected').val(),
				'sic': $("input[name=sic]:checked").val(),
				'postal_code': $('#postal_code').val()}).then(function(data){
					
					check_tester_free = data
				});
			}, 1000);
				
				setTimeout(function(){
				if (check_tester_free[0] == 'penalty'){
					$('.error_tester_penalty').css('display', 'block');
					$('#booking_send_special_request').modal('show');
				}
				else{
					if (check_tester_free[0] == false){
						$('#booking_send_special_request').modal('hide');
						setTimeout(function(){
						$('#booking_confirmation_special').modal('show');
						$('#booking_special_point').html(QWeb.render('booking_picker_special_div', {
							'pr_name': pr_name,
							'cust_name': cust_name,
							'pr_id': $('#project option:selected').val(),
							'cust_id': $('#customer option:selected').val(),
							'co_name': $('#Contact').val(),
							'co_no': $('#con_no').val(),
							'sic': sic,
							'start_date': $('#start_date').val(),
							'st_time': st_time,
							'en_time': en_time,
							'tester_id': '',
							'tester_name': '',
							'tester_contact': '',
							'add_accept_button': true,
							'end_date': $('#end_date').val(),
							'new_pr_result': new_pr_result,
							'backend_st_dt': backend_st_dt,
							'backend_ed_dt': backend_ed_dt,
							'address': $('#address').val(),
							'postal_code': $('#postal_code').val(),
							'created_anchor': Object.values(created_anchor),
				          }))
						}, 500);
					}
					else{
						$('#booking_send_special_request').modal('hide');
						setTimeout(function(){
						$('#booking_confirmation_special').modal('show');
						$('#booking_special_point').html(QWeb.render('booking_picker_special_div', {
							'pr_name': pr_name,
							'cust_name': cust_name,
							'pr_id': $('#project option:selected').val(),
							'cust_id': $('#customer option:selected').val(),
							'co_name': $('#Contact').val(),
							'co_no': $('#con_no').val(),
							'sic': sic,
							'start_date': $('#start_date').val(),
							'st_time': st_time,
							'en_time': en_time,
							'tester_id': check_tester_free[0],
							'tester_name': check_tester_free[1],
							'tester_contact': check_tester_free[2],
							'add_accept_button': false,
							'end_date': $('#end_date').val(),
							'new_pr_result': new_pr_result,
							'backend_st_dt': backend_st_dt,
							'backend_ed_dt': backend_ed_dt,
							'address': $('#address').val(),
							'postal_code': $('#postal_code').val(),
							'created_anchor': Object.values(created_anchor),
				          }))
						}, 500);
					}
					}
				}, 1500);
			}
			else{
                $('.button_date_special').attr("data-dismiss", "false");
			}
            check_attr_right_arrow()
		});
		
		$(".button_date_sic").click(function(){
			var sic_not_goen = false;
			function formatDate(date) {
			    var d = new Date(date),
			        month = '' + (d.getMonth() + 1),
			        day = '' + d.getDate(),
			        year = d.getFullYear();

			    if (month.length < 2) month = '0' + month;
			    if (day.length < 2) day = '0' + day;

			    return [day, month, year].join('/');
			}
			
			var sic = false;
			if ($('#project option:selected').val()){
				var pr_name = $('#project option:selected').text();
			}
			else{
				var pr_name = $('#project option:selected').val();
			}
			if ($("input[name=sic]:checked").val() == 'yes'){
				sic = "Yes"
			}
			if ($("input[name=sic]:checked").val() == 'no'){
				sic = "No"
			}
			if ($('#customer option:selected').val()){
				var cust_name = $('#customer option:selected').text();
			}
			else{
				var cust_name = $('#customer option:selected').val();
			}
			if ($('#st_time_sic').val()){
				$('.sic_start_time_error')
                .css('display', 'none');
				var time = $('#st_time_sic').val();
				var hours = Number(time.match(/^(\d+)/)[1]);
				var minutes = Number(time.match(/:(\d+)/)[1]);
				var AMPM = time.match(/\s(.*)$/)[1].toLowerCase();

				if (AMPM == "pm" && hours < 12) hours = hours + 12;
				if (AMPM == "am" && hours == 12) hours = hours - 12;
				var sHours = hours.toString();
				var sMinutes = minutes.toString();
				if (hours < 10) sHours = "0" + sHours;
				if (minutes < 10) sMinutes = "0" + sMinutes;
				var st_time = sHours +':'+sMinutes
				if ($('#start_date_sic').val()){
					$('.sic_start_date_error')
	                .css('display', 'none');
					var backend_st_dt = $('#start_date_sic').val() + ' ' + st_time + ':' + '00'
				}
				else{
					$('.sic_start_date_error')
	                .css('display', 'block');
					sic_not_goen = true;
				}
			}
			else {
				$('.sic_start_time_error')
                .css('display', 'block');
				sic_not_goen = true;
				var st_time = ''
					var backend_st_dt = $('#start_date_sic').val() + ' ' + '00:00' + ':' + '00'
			}
			if ($('#ed_time_sic').val()){
				$('.sic_end_time_error')
                .css('display', 'none');
				var time = $('#ed_time_sic').val();
				var hours = Number(time.match(/^(\d+)/)[1]);
				var minutes = Number(time.match(/:(\d+)/)[1]);
				var AMPM = time.match(/\s(.*)$/)[1].toLowerCase();

				if (AMPM == "pm" && hours < 12) hours = hours + 12;
				if (AMPM == "am" && hours == 12) hours = hours - 12;
				var sHours = hours.toString();
				var sMinutes = minutes.toString();
				if (hours < 10) sHours = "0" + sHours;
				if (minutes < 10) sMinutes = "0" + sMinutes;
				var en_time = sHours +':'+sMinutes
				var backend_ed_dt = $('#start_date_sic').val() + ' ' + en_time + ':' + '00'
			}
			else {
				$('.sic_end_time_error')
                .css('display', 'block');
				sic_not_goen = true;
				var en_time = ''
				var backend_ed_dt = $('#start_date_sic').val() + ' ' + '00:00' + ':' + '00'
			}
			
			
			var check_tester_free = false;
			if (sic_not_goen == false){
				
				ajax.jsonRpc("/sic_request_tester", 'call', {'booking_date': $('#start_date_sic').val(),
					'start_time': st_time, 'end_time': en_time, 'postal_code': $('#postal_code').val()}).then(function(data){
						check_tester_free = data
					});
				setTimeout(function(){
					if (check_tester_free[0] == 'penalty'){
						$('.error_tester_penalty_sic').css('display', 'block');
						$('#booking_sic_request').modal('show');
					}
					else{
						if (check_tester_free[0] == false){
							$('.error_tester_notavailable_sic').css('display', 'block');
							$('#booking_sic_request').modal('show');
						}
						else{
							$('#booking_sic_request').modal('hide');
							setTimeout(function(){
							$('#booking_confirmation_sic').modal('show');
							$('#booking_sic_point').html(QWeb.render('booking_picker_sic_div', {
								'pr_name': pr_name,
								'cust_name': cust_name,
								'pr_id': $('#project option:selected').val(),
								'cust_id': $('#customer option:selected').val(),
								'co_name': $('#Contact').val(),
								'co_no': $('#con_no').val(),
								'sic': sic,
								'tester_id': check_tester_free[0],
								'tester_name': check_tester_free[1],
								'tester_contact': check_tester_free[2],
								'start_date': $('#start_date_sic').val(),
								'st_time': st_time,
								'en_time': en_time,
								'end_date': $('#start_date_sic').val(),
								'backend_st_dt': backend_st_dt,
								'backend_ed_dt': backend_ed_dt,
								'address': $('#address').val(),
								'postal_code': $('#postal_code').val(),
					          }))
							}, 500);
						}
					}
				}, 1500);
			}
			else{
				$('.button_date_sic').attr("data-dismiss", "false");
			}
            check_attr_right_arrow()
		});
		
		
		$(".button_book_book").click(function(){
			var sic = false
			var all_anchor = []
			var created_anchor = [];
			var an_counter = $('#anchor_count').val();
			if ($('#anchor_size option:selected').val()){
				var an_size = $('#anchor_size option:selected').val();
			}
			else{
				var an_size = $('#anchor_size option:selected').val();
			}
			if ($('#anchor_type option:selected').val()){
				var an_type = $('#anchor_type option:selected').val();
			}
			else{
				var an_type = $('#anchor_type option:selected').val();
			}
			var an_qty = $('#anhor_qty').val()
			var radioValue = $("input[name='complexity']:checked").val();
			all_anchor.push([an_size, an_type, an_qty])
			ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size, 'an_type': an_type, 'an_qty': an_qty, 'redio_val': radioValue, 'an_name': 1}).then(function(results){
				created_anchor.push(parseInt(results))
			});

			for (var i = 2; i <= an_counter; i++) {
				if ($('#anchor_type_'+i+' option:selected').val()){
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				else{
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				if ($('#anchor_size_'+i+' option:selected').val()){
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				else{
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				var an_qty_1 = $('#anhor_qty_'+i+'').val()
				all_anchor.push([an_size_1, an_type_1, an_qty_1])
				var radioValue = $("input[name='complexity_"+i+"']:checked").val();
				ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size_1, 'an_type': an_type_1, 'an_qty': an_qty_1, 'redio_val': radioValue, 'an_name': i}).then(function(results){
					created_anchor.push(parseInt(results))
				});
			}
			
			setTimeout(function(){
			ajax.jsonRpc("/user_book_slot", 'call', {}).then(function(results){
				var open_popup = false;
				if (results[0].start == false || results[0].end == false || results[0].start_time == false || results[0].end_time == false || results[0].Booking_date == false){
					open_popup = true;
				}
				
				if (results[0].start >= 12){
					var start = results[0].start_time + " " + 'PM'
				}
				else{
					var start = results[0].start_time + " " + 'AM'
				}
				if (results[0].end >= 12){
					var end = results[0].end_time + " " + 'PM'
				}
				else{
					var end = results[0].end_time + " " + 'AM'
				}
				if (results[0].start && results[0].end){
					var final_start_end = start + " - " + end
				}
				else{
					var final_start_end = ''
				}
				if ($('#customer option:selected').val()){
					var cust_name = $('#customer option:selected').text();
				}
				else{
					var cust_name = $('#customer option:selected').val();
				}
				if ($('#project option:selected').val()){
					var pr_name = $('#project option:selected').text();
				}
				else{
					var pr_name = $('#project option:selected').val();
				}
				if ($("input[name=sic]:checked").val() == 'yes'){
					sic = "Yes"
				}
				if ($("input[name=sic]:checked").val() == 'no'){
					sic = "No"
				}
				if (open_popup == false){
					$('.select_calendar_error')
                    .css('display', 'none');
					$('#booking_confirmation').modal('show');
					$('#booking_point').html(QWeb.render('booking_picker_div', {
						'cust_name': cust_name,
						'pr_name': pr_name,
						'cust_id': $('#customer option:selected').val(),
						'pr_id': $('#project option:selected').val(),
						'co_name': $('#Contact').val(),
						'co_no': $('#con_no').val(),
						'sic': sic,
						'booking_type': 'normal',
						'requested_time': false,
						'b_date': results[0].Booking_date,
						'tester_name': results[0].tester_name,
						'tester_phone': results[0].tester_contact,
						'b_time': final_start_end,
						'new_pr_result': new_pr_result,
						'tm_id': results[0].time_slot_booking,
						'address': $('#address').val(),
						'postal_code': $('#postal_code').val(),
						'created_anchor': Object.values(created_anchor),
			        }))
				}
				else{
					$('.select_calendar_error')
                    .css('display', 'block');
				}
			});
			}, 500);
            check_attr_right_arrow()

		});
		
		$(".button_book_special_a").click(function(){
			$('#start_date').val('');
			$('#end_date').val('');
			$('#st_time').val('10:30 AM');
			$('#ed_time').val('10:30 AM');
			var testing = 0;
			var pr_id =  $('#project option:selected').val();
			$('.error_tester_notavailable').css('display', 'none');
			setTimeout(function(){
				if (testing == 0){
					$('#booking_send_special_request').modal('show');
				}
			}, 50);
		});
		
		$('.timepicker1').timepicker();
		$('.datePicker').datepicker({ dateFormat: 'dd-mm-yy' });
		$(".redirect_page_class").click(function(){
			window.location.href = "/booking";
		});
		
		$(".open_terms_condition").click(function(){
			$('#terms_and_condition').modal('show');
		});
		
		$(".open_terms_and_condition_policy").click(function(){
			$('#terms_and_condition_policy').modal('show');
			
		});
		
		
		jQuery(document).on('click', '.time_s', function() {
			var $this = $(this);
            $this.css("background-color", "#19AF37");
            ajax.jsonRpc("/create_time_slot", 'call', {'date': $('#hidden_selected_date').val(), 'time_slot_id': $(this).find('#time_slot_id').val(), 'tester_id': $(this).find('#tester_id').val()}).then(function(results){
            setTimeout(function(){
				$('#time_slot').modal('hide');
			}, 500);
            });
            
            
		});
		
        var calendar = $('#website_calendar').fullCalendar({
        	
            slotLabelFormat: 'hh:mma',
            defaultView: 'month',
            timezone: 'local',
            allDaySlot: false,
            selectable: true,

            header:{
                left: 'prev',
                center: 'title',
                right: 'next',
                // right: 'agendaDay, agendaWeek, month',
            },
            firstDay: 1,
            height: 450,
            
            viewRender: function(currentView){
            	ajax.jsonRpc("/total_month_display", 'call', {}).then(function(data){
	                  if (data){
	                	  if (data != 0){
	                      	var minDate = moment(),
	                  		maxDate = moment().add(data,'months');
	                  		// Past
	                  		if (minDate >= currentView.start && minDate <= currentView.end) {
	                  			$(".fc-prev-button").prop('disabled', true); 
	                  			$(".fc-prev-button").addClass('fc-state-disabled'); 
	                  		}
	                  		else {
	                  			$(".fc-prev-button").removeClass('fc-state-disabled'); 
	                  			$(".fc-prev-button").prop('disabled', false); 
	                  		}
	                  		// Future
	                  		if (maxDate >= currentView.start && maxDate <= currentView.end) {
	                  			$(".fc-next-button").prop('disabled', true); 
	                  			$(".fc-next-button").addClass('fc-state-disabled'); 
	                  		} else {
	                  			$(".fc-next-button").removeClass('fc-state-disabled'); 
	                  			$(".fc-next-button").prop('disabled', false); 
	                  		}
	                      }
	                	  }
	              }) 
        	},
            
	        dayRender: function (date, cell) {
	        	var cellYear = date.year();
	        	var cellMonth = date.month() + 1;
	        	var cellDay = date.date();
	        	var today = new Date();
	        	var total_slot = []
	            ajax.jsonRpc("/holydays", 'call', {'date':cellDay,'cellMonth':cellMonth,'cellYear':cellYear}).then(function(data){
	                  if (data && data[0]){
	                	  if (data[0] == '1'){
//	                		  cell.css("background-color", "#d2d3d5");
	                		  cell.css("background-color", "#dfd7ca");
	                		  cell.addClass("off_class");
	                	  }
	                  }
	              })
	        },
            
          dayClick: function(date, allDay, jsEvent, view) {
        	  var $this = $(this);
        	  var cellYear = date.year();
        	  var cellMonth = date.month() + 1;
        	  var cellDay = date.date();
        	  var total_slot = []
        	  var temp = 0;
        	  if ($("input[name=sic]:checked").val() == 'yes'){
                   if ($('#re_time_sic_hours').val() && $('#re_time_sic_minutes').val()) {
                     $('.re_time_sic_error').css('display', 'none');
                   }else{
                     $('.re_time_sic_error').css('display', 'block');
                     return false
                  }
              }
        	  if ($(this).hasClass('off_class')) {
        		  temp = 1;
        	  }
        	  if ($(this).hasClass('fc-sat')) {
        		  temp = 1;
        	  }
        	  if ($(this).hasClass('fc-sun')) {
        		  temp = 1;
        	  }
        	  if ($(this).hasClass('fc-past')) {
        		  temp = 1;
        	  }
        	  var testing = 0;
	  		  var pr_id =  $('#project option:selected').val();
	  			
        	  var total_hours = []
        	  var all_anchors = []
	    	  var an_counter = $('#anchor_count').val();
	  		  var radioValue = $("input[name='complexity']:checked").attr('data');
	  		  if ($('#anchor_size option:selected').val()){
	  			  var an_size = $('#anchor_size option:selected').val();
	  		  }
	  		  else{
	  			  var an_size = $('#anchor_size option:selected').val();
	  		  }
	  		  if ($('#anchor_type option:selected').val()){
	  			  var an_type = $('#anchor_type option:selected').val();
	  		  }
	  		  else{
	  			  var an_type = $('#anchor_type option:selected').val();
	  		  }
	  		  all_anchors.push([String(an_size),String(an_type)])
	  		  var an_qty = $('#anhor_qty').val();
	  		  total_hours.push(String(parseFloat(radioValue) * parseFloat(an_qty)))
	  		  for (var i = 2; i <= an_counter; i++) {
				var radioValue1 = $("input[name='complexity_"+i+"']:checked").attr('data');
				var an_qty_1 = $('#anhor_qty_'+i+'').val();
				total_hours.push(String(parseFloat(radioValue1) * parseFloat(an_qty_1)))
				if ($('#anchor_type_'+i+' option:selected').val()){
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				else{
					var an_type_1 = $('#anchor_type_'+i+' option:selected').val();
				}
				if ($('#anchor_size_'+i+' option:selected').val()){
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				else{
					var an_size_1 = $('#anchor_size_'+i+' option:selected').val();
				}
				all_anchors.push([String(an_size_1),String(an_type_1)])
	  		  }
        	  $('.fc-month-view').find('td.back_color_selected').removeClass('back_color_selected');
        	  if (new_pr_result == 1){
	        		  setTimeout(function(){
			        	  if (temp == 0){
			        		  if (testing == 0){
				                  $this.addClass('back_color_selected');
				        		  var date1 = new Date(date.year(), date.month() + 1, date.date());
//				        		  ajax.jsonRpc("/all_slot", 'call', {'date':cellDay,'cellMonth':cellMonth,'cellYear':cellYear, 'total_hours': $('#re_time_sic').val(), 'all_anchors': ['sic_booking'], 'project_id': $('#project option:selected').val(), 'sic': $("input[name=sic]:checked").val(), 'postal_code': $('#postal_code').val()}).then(function(data){
				        		  ajax.jsonRpc("/all_slot", 'call', {'date':cellDay,'cellMonth':cellMonth,'cellYear':cellYear, 'total_hours': $('#re_time_sic_hours').val() +':'+  $('#re_time_sic_minutes').val(), 'all_anchors': ['sic_booking'], 'project_id': $('#project option:selected').val(), 'sic': $("input[name=sic]:checked").val(), 'postal_code': $('#postal_code').val()}).then(function(data){
				            		  if (data[0] == 'penalty'){
				                    	  $('#time_slot').modal('show')
					                      var is_blanck = false;
					                      if (data[0].length == 0){
					                    	  is_blanck = true;
					                      }
					                	  $('#timeslot_with_error').html(QWeb.render('time_picker', {
					            			  'total_slot': false,
					                		  'selected_date': false,
					                		  'time_slot_based': false,
					                		  'is_blanck': false,
					                		  'is_penalty': true,
					                		  'massage': data[1]
					        	          }))
				                      }
				                      else{
					            		  $('#time_slot').modal('show')
					                      var is_blanck = false;
					                      if (data[0].length == 0){
					                    	  is_blanck = true;
					                      }
					                	  $('#timeslot_with_error').html(QWeb.render('time_picker', {
					            			  'total_slot': data[0],
					                		  'selected_date': data[1],
					                		  'time_slot_based': data[2],
					                		  'is_blanck': is_blanck,
					                		  'is_penalty': false,
					                		  'massage': false,
					        	          }))
				                      }
				                  });
			        		  }
			        		  
			        	  }
			        	  else{
			        		  return false;
			        	  }
		        	  }, 500);
        	  }
        	  else{
	        	  setTimeout(function(){
		        	  if (temp == 0){
		        		  if (testing == 0){
		        			  $('.select_calendar_error')
		                      .css('display', 'none');
			                  $this.addClass('back_color_selected');
			        		  var date1 = new Date(date.year(), date.month() + 1, date.date());
			            	  ajax.jsonRpc("/all_slot", 'call', {'date':cellDay,'cellMonth':cellMonth,'cellYear':cellYear, 'total_hours': total_hours, 'all_anchors': all_anchors, 'project_id': $('#project option:selected').val(), 'sic': $("input[name=sic]:checked").val(), 'postal_code': $('#postal_code').val()}).then(function(data){
			            		  if (data[0] == 'penalty'){
			                    	  $('#time_slot').modal('show')
				                      var is_blanck = false;
				                      if (data[0].length == 0){
				                    	  is_blanck = true;
				                      }
				                	  $('#timeslot_with_error').html(QWeb.render('time_picker', {
				            			  'total_slot': false,
				                		  'selected_date': false,
				                		  'time_slot_based': false,
				                		  'is_blanck': false,
				                		  'is_penalty': true,
				                		  'massage': data[1]
				        	          }))
			                      }
			                      else{
				            		  $('#time_slot').modal('show')
				                      var is_blanck = false;
				                      if (data[0].length == 0){
				                    	  is_blanck = true;
				                      }
				                	  $('#timeslot_with_error').html(QWeb.render('time_picker', {
				            			  'total_slot': data[0],
				                		  'selected_date': data[1],
				                		  'time_slot_based': data[2],
				                		  'is_blanck': is_blanck,
				                		  'is_penalty': false,
				                		  'massage': false,
				        	          }))
			                      }
			                  });
		        		  }
		        		  
		        	  }
		        	  else{
		        		  return false;
		        	  }
	        	  }, 500);
        	  }
            },
            
            
            monthNamesShort: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
            monthNames: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
            
            editable: true,
        });

	});

});

