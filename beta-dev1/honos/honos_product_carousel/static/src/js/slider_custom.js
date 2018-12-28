function create_slider(slider_slide,slider_name){
	var slide_int_val=parseInt(slider_slide);
	
	if ($(slider_name).find(".fun_slide_class").size() <= slide_int_val){
		$(slider_name).find(".fun_slide_class").css({"width": 92/slide_int_val +"%" ,"float": "left","display": "block","margin":"1%","padding":"1%","position":"relative"});
	}
	else{
		  $(slider_name).bxSlider({
				mode : 'horizontal',
				auto : true,
				speed : 600,
				infiniteLoop: true,
				controls : true,
				slideWidth : 800,
				autoControls: true,
				minSlides : 4,
				maxSlides : 4,
				moveSlides : 1,
				slideMargin :50,
				responsive:true,
		  });
	}
	if ($(window).width() <= 360) {  
		   $(slider_name).bxSlider({
			   
			   slideWidth : 270,
			   minSlides : slide_int_val,
			   maxSlides : 1,
			   slideMargin: 20,
		   });

	}     

	
	
}


	

