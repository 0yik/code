$(window).load(function(){
	
	 if($(window).width() < 800)
	{
	  $('.bxslider.recentbx').bxSlider({
	  minSlides: 2,
	  maxSlides: 2,
	  slideWidth:400,
	  slideMargin: 10,
	  moveSlides: 1,
	  infiniteLoop: false,
	  speed : 600,
	  auto:true,
	  autoControls: true,
	  autoHover:true,
	  responsive:true,
	  pager:false,
	});
	}
  
	$('.bxslider.recentbx').bxSlider({
	  minSlides: 4,
	  maxSlides: 4,
	  slideWidth:400,
	  slideMargin: 10,
	  moveSlides: 1,
	  infiniteLoop: false,
	  speed : 600,
	  auto:true,
	  autoControls: true,
	  autoHover:true,
	  responsive:true,
	  pager:false,
  });
 
	$('.bx-pager').css("display","none");
	var $applyied_sldier = $(".bxslider");
	if($applyied_sldier){
	var a = $(".recently_viewed_for_products").find("img").width();
	$(".recently_viwed_details").css("width",a);
	};

	var suggest_count = $('.suggest_count').html();
	if(suggest_count > 2){
		$('#suggested_item_product > .bxslider').bxSlider({
			  minSlides: 2,
			  maxSlides: 2,
			  slideWidth:400,
			  slideMargin: 10,
			  moveSlides: 1,
			  infiniteLoop: false,
			  speed : 600,
			  auto:true,
			  autoControls: true,
			  autoHover:true,
			  responsive:true,
			  pager:false,
		  });
		  $('.bx-pager').css("display","none");
	}
	var acce_count = $('.acce_count').html();
	if(acce_count > 2){
		$('#acce_item_product > .bxslider').bxSlider({
			  minSlides: 2,
			  maxSlides: 2,
			  slideWidth:400,
			  slideMargin: 10,
			  moveSlides: 1,
			  infiniteLoop: false,
			  speed : 600,
			  auto:true,
			  autoControls: true,
			  autoHover:true,
			  responsive:true,
			  pager:false,
		  });
		  $('.bx-pager').css("display","none");
	}
});
	
