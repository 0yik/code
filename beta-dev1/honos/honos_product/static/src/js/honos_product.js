
$(window).load(function() {
	//zooming effect of video icon
	var animDuration = 500;
	$(".pvideo_link").addClass("i-zoom-animation");
    setTimeout(function(){
    $(".pvideo_link").removeClass("i-zoom-animation");
    }, animDuration
    );
});
$(document).ready(function() {  
	$(".pvideo_link").click(function(){ 
		$('.product_video_popup_main').css("display","block");
		$("iframe.popup_iframe_url").attr('src', $("iframe.popup_iframe_url").attr('src') + "?autoplay=1&amp;controls=0&amp;loop=1&amp;rel=0&amp;showinfo=0");
		$('body').css("overflow","hidden");
	})
	$(".popup-close").click(function(){ 
		$('.product_video_popup_main').css("display","none");
		$('body').css("overflow","visible");
	})
})

 
$(document).on( 'keydown', function(e){
	if(e.keyCode === 27) {
		$('.product_video_popup_main').css("display","none");
		$('body').css("overflow","visible");
	}
});	
