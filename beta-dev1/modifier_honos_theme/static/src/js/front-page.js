$('document').ready(function(){

    var boxWidth = $(".right_top").height();
    var bottombox = $(".right_bottom").height();
    var topim = $(".rtop_image_img").height();
    var botim = $(".rbot_image_img").height();
    console.log("Sssssss",bottombox);
    
    
    $('.js_add_cart_json').addClass('disabled');
    $('.oe_website_spinner input').attr('disabled','true');


    // $('.front_left').css('z-index', '0',
    // 'position', 'absolute',
    // 'transition-property', 'width, height, top, left',
    // 'left', '0%',
    // 'top', '0%',
    // 'width', '100%',
    // 'height', '100%')
    // console.log('jjjjj  '+$('.front_left').width())

    $('.front_left').click(function(e){
    	$('.front_left').addClass('full_width');
    	$(".front_right").addClass('hidden');
    	$(".video_block").removeClass('hidden');
    	$(this).addClass('hidden');
    });
    
    $('.video_block .fa-times, .video_block #small_logo').click(function(e){
    	$('.front_left').removeClass('full_width');
    	// window.reload()
    	$(".front_right").removeClass('hidden');
    	$(".video_block").addClass('hidden');
    	$(".front_left").removeClass('hidden');
    	$(this).parent().addClass('hidden');
    });


	// setTimeout(function(){
	// 	// var totla_height = $('.front_left').height();
	// 	$('.front_left').animate({
	// 	    width: "60%",
	// 	});
	// 	$('.front_right').animate({
	// 	    width: "40%",
	// 	    // height:totla_height,
	// 	});
	// },300);

    $(".right_top").mouseenter(function(){
        $(this).animate({
            height: "450px",
        });
        $(".right_bottom").animate({
            height: bottombox - 66 + "px",
        });
        $(".rtop_image_img").animate({
            height: topim + 66 + "px",
        });
         $(".rbot_image_img").animate({
            height: botim -66 +"px",
        });
    }).mouseleave(function(){
        $(this).animate({
            height: boxWidth
        });
        $(".right_bottom").animate({
            height: bottombox,
        });
        $(".rtop_image_img").animate({
            height: topim,
        });
    });


    $(".right_bottom").mouseenter(function(){
        $(this).animate({
            height: "450px",
        });
        $(".right_top").animate({
            height: boxWidth - 66 + "px",
        });
        $(".rbot_image_img").animate({
            height: topim + 66 + "px",
        });
    }).mouseleave(function(){
        $(this).animate({
            height: bottombox
        });
        $(".right_top").animate({
            height: boxWidth,
        });
        $(".rbot_image_img").animate({
            height: botim,
        });
    });
    
    // for timer snippet block
    /* now we have backend configured tracker
    if ($('.snippet_right_timer_div').length >0){
	    var timer;
	    var compareDate = new Date();
	    compareDate.setDate(compareDate.getDate() + 7);
	    timer = setInterval(function() {
	      timeBetweenDates(compareDate);
	    }, 1000);
	    
	    function timeBetweenDates(toDate) {
	    	var dateEntered = toDate;
	    	var now = new Date();
	    	var difference = dateEntered.getTime() - now.getTime();
	    	if (difference <= 0) {
		        clearInterval(timer);
	    	} else {
		        var seconds = Math.floor(difference / 1000);
		        var minutes = Math.floor(seconds / 60);
		        var hours = Math.floor(minutes / 60);
		        var days = Math.floor(hours / 24);
		        hours %= 24;
		        minutes %= 60;
		        seconds %= 60;
		        $("#days").text(days);
		        $("#hours").text(hours);
		        $("#minutes").text(minutes);
		        $("#seconds").text(seconds);
	    	}
	    }
    }
    */
    
    $(".filter").click(function(){
		var value = $(this).attr('data-filter');
		
		if(value == "all")
		{
			$('.filter_img').show('1000');
		}
		else
		{
			$(".filter_img").not('.'+value).hide('3000');
			$('.filter_img').filter('.'+value).show('3000');
			
		}
	});
	$('.filter_menu ul li').click(function(){
		$('li.filter').removeClass("active");
		$(this).addClass("active");
	});

	var url = window.location.search;
	url = url.replace("?", '');
	if ($(".filter_menu").length > 0){
		$(".filter_menu > ul").find("[data-filter='" + url + "']").trigger( "click" );
	}
	
});