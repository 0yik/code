odoo.define('hilti_modifier_customer_booking.hilti_modifier_customer_booking', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;
    var new_pr_result = 0;
    ajax.loadXML("/hilti_modifier_customer_booking/static/src/xml/hilti_booking_templates_view.xml", core.qweb);
    ajax.loadXML("/hilti_modifier_customer_booking/static/src/xml/booking_time_slot1.xml", core.qweb);
    var QWeb = core.qweb;
	$(document).ready(function() {
		$('.sic').change(function() {
			if ($(this).attr('value') == 'yes'){
				$('.left_arrow').css('display', 'none');
				$('.booking_page').css('display', 'block');
				$('#anchor_portion').css('display', 'block');
				$('#calendar_portion').css('display', 'block');
				var pr_id =  $('#project option:selected').val();
				ajax.jsonRpc("/check_project_is_new", 'call', {'project_id': pr_id}).then(function(results){
					if (results == 1){
						new_pr_result = 1
						$('.book_for_sic').css('display', 'block');
						$('#anchor_portion').css('display', 'none');
						$('#calendar_portion').css('display', 'none');
					}
					else {
						new_pr_result = 0
						$('.book_for_sic').css('display', 'none');
					}
				});
				
			}
			if ($(this).attr('value') == 'no'){
				$('.left_arrow').css('display', 'block');
				$('.booking_page').css('display', '-webkit-box');
				$('#anchor_portion').css('display', 'none');
				$('#calendar_portion').css('display', 'none');
				$('.book_for_sic').css('display', 'none');
			}
		});
		
		$(document).ready(function (e) {
		     $("#booking_right_arrow").click(function (e) {
		    	 $("#booking_portion").animate({width:'toggle'},350 );
		    	 $("#anchor_portion").animate({width:'toggle'},350);
		     });
		     $("#anchor_left_arrow").click(function (e) {
		    	 $("#anchor_portion").animate({width:'toggle'},350);
		         $("#booking_portion").animate({width:'toggle'},350 );        
		     });
		     
		     $("#anchor_right_arrow").click(function (e) {
		    	 $("#anchor_portion").animate({width:'toggle'},350);
		    	 $("#calendar_portion").animate({width:'toggle'},350);
		     });
		     $("#calendar_left_arrow").click(function(e){
		    	 $("#calendar_portion").animate({width:'toggle'},350);
		    	 $("#anchor_portion").animate({width:'toggle'},350 );
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
		
		$('.special_checkbox').change(function() {
		    if (this.checked) {
		        // the checkbox is now checked 
		    	$(".special_submit_bottom").removeAttr('disabled');
		    } else {
		        // the checkbox is now no longer checked
		    	$(".special_submit_bottom").attr("disabled", "disabled")
		    }
		});
		

		
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
		
		jQuery(document).on('change', '.js_anchor_type_auto', function() {
    		var item = $(this).val();
    		var co = $(this).attr('index');
    		if (item){
    			$("#anchor_size_"+String(co)+" option:not([value=''])").remove();
		    	$('#small_'+String(co) +'> img').remove();
		    	$('#medium_'+String(co) +'> img').remove();
		    	$('#complex_'+String(co) +'> img').remove();
		    	ajax.jsonRpc("/get_anchor_size", 'call', {'selected_id': item}).then(function(anchor_size){
		    		_.each(anchor_size[0], function(size) {
		    			$('#anchor_size_'+String(co)).children("option").eq(0).after('<option value="'+size.id+'">'+size.name+'</option> ');
		    		});
		    		$('#small_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[1]+'" class="img-responsive img-radio" />');
		    		$('#medium_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[2]+'" class="img-responsive img-radio" />');
		    		$('#complex_'+String(co)).prepend('<img src="data:image/png;base64,'+anchor_size[3]+'" class="img-responsive img-radio" />');
		    	});
		    	$('#display_none_sitecondition_'+String(co)).css('display', 'block');
		    }
		    else{
		    	$('#display_none_sitecondition_'+String(co)).css('display', 'none');
		    	$("#anchor_size_"+String(co)+" option:not([value=''])").remove();
		    }
    	});

	    jQuery(document).on('click', '.remove_this', function() {
	    	var an_counter = $('#anchor_count').val();
	    	$("#anchor_count").val(parseInt(an_counter) - 1)
	    	$("#anchor_"+String(parseInt($('#anchor_count').val())-1)).children().eq(0).before('<a class="remove_this fa fa-remove" style="color: #d2051e;cursor: pointer;">&amp;Remove</a>');
	        jQuery(this).parent('.anchor_main').remove();
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
		    		$('.small').prepend('<img src="data:image/png;base64,'+anchor_size[1]+'" class="img-responsive img-radio" />');
		    		$('.medium').prepend('<img src="data:image/png;base64,'+anchor_size[2]+'" class="img-responsive img-radio" />');
		    		$('.complex').prepend('<img src="data:image/png;base64,'+anchor_size[3]+'" class="img-responsive img-radio" />');
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
				location.reload();
			}, 1000);
			
		});
		
		
		$(".button_book_sic").click(function(){
			$('#calendar_portion').css('display', 'block');
			$('.book_for_sic').css('display', 'none');
		});
		
		$(".button_date_special").click(function(){
			var all_anchor = [];
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
			var radioValue = $("input[name='complexity']:checked").val();
			var an_qty = $('#anhor_qty').val()
			all_anchor.push([an_size, an_type, an_qty])
			ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size, 'an_type': an_type, 'an_qty': an_qty, 'an_name': 1}).then(function(results){
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
				ajax.jsonRpc("/create_anchor_project", 'call', {'an_size': an_size_1, 'an_type': an_type_1, 'an_qty': an_qty_1, 'an_name': i}).then(function(results){
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
			if ($('#st_time').val()){
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
				var backend_st_dt = $('#start_date').val() + ' ' + st_time + ':' + '00'
			}
			else {
				var st_time = ''
					var backend_st_dt = $('#start_date').val() + ' ' + '00:00' + ':' + '00'
			}
			if ($('#ed_time').val()){
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
				var backend_ed_dt = $('#end_date').val() + ' ' + en_time + ':' + '00'
			}
			else {
				var en_time = ''
				var backend_ed_dt = $('#end_date').val() + ' ' + '00:00' + ':' + '00'
			}
			setTimeout(function(){
			$('#booking_confirmation_special').modal('show');
			$('#booking_special_point').html(QWeb.render('booking_picker_special_div', {
				'pr_name': pr_name,
				'pr_id': $('#project option:selected').val(),
				'co_name': $('#Contact').val(),
				'co_no': $('#con_no').val(),
				'sic': sic,
				'start_date': $('#start_date').val(),
				'st_time': st_time,
				'en_time': en_time,
				'end_date': $('#end_date').val(),
				'new_pr_result': new_pr_result,
				'backend_st_dt': backend_st_dt,
				'backend_ed_dt': backend_ed_dt,
				'address': $('#address').val(),
				'postal_code': $('#postal_code').val(),
				'created_anchor': Object.values(created_anchor),
	          }))
			}, 500);
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
				$('#booking_confirmation').modal('show');
				$('#booking_point').html(QWeb.render('booking_picker_div', {
					'pr_name': pr_name,
					'pr_id': $('#project option:selected').val(),
					'co_name': $('#Contact').val(),
					'co_no': $('#con_no').val(),
					'sic': sic,
					'b_date': results[0].Booking_date,
					'b_time': final_start_end,
					'new_pr_result': new_pr_result,
					'tm_id': results[0].time_slot_booking,
					'address': $('#address').val(),
					'postal_code': $('#postal_code').val(),
					'created_anchor': Object.values(created_anchor),
		        }))
			});
			}, 500);
			
		});
		
		$(".button_book_special_a").click(function(){
			$('#start_date').val('');
			$('#end_date').val('');
			$('#booking_send_special_request').modal('show');
		});
		
		$('.timepicker1').timepicker();
		$('.datePicker').datepicker({ dateFormat: 'mm-dd-yy' });
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
            $this.css("background-color", "#671a3e");
            ajax.jsonRpc("/create_time_slot", 'call', {'date': $('#hidden_selected_date').val(), 'time_slot_id': $(this).find('#time_slot_id').val()}).then(function(results){
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
	                		  cell.css("background-color", "#d2d3d5");
	                		  cell.addClass("off_class");
	                	  }
	                  }
	                  if (data && data[1]){
	                	  if (data[1] == '10'){
	                		  cell.css("background-color", "#d2051e");
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
        	  $('.fc-month-view').find('td.back_color_selected').removeClass('back_color_selected');
        	  if (temp == 0){
                  $this.addClass('back_color_selected');
        		  var date1 = new Date(date.year(), date.month() + 1, date.date());
            	  ajax.jsonRpc("/all_slot", 'call', {'date':cellDay,'cellMonth':cellMonth,'cellYear':cellYear}).then(function(data){
                      $('#time_slot').modal('show')
                	  $('#time_slot_point').html(QWeb.render('time_picker', {
            			  'total_slot': data[0],
                		  'selected_date': data[1],
        	          }))
                  });
        	  }
        	  else{
        		  return false;
        	  }
            },
            
            
            monthNamesShort: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
            monthNames: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
            
            editable: true,
        });
		
	});

});

