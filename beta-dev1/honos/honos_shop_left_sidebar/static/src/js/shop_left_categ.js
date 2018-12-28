$(document).ready(function(){
	//var find_var = $('body').find('.oe_shop_left');
	if($('div').hasClass('oe_shop_left'))
		{
			$("div").find(".main").addClass("main_left");
			$("div").find("#products_grid").addClass("main_left_grid");
			$("div").find("#products_grid_before").addClass("main_left_grid_before");
			$("div").find(".right-cnt-maxW").addClass("right-cnt-maxW_left");
			//$("div").find(".products-grid-main").removeClass("main_left_grid");
			$(".menu-filter").unbind("click"); 
			$('.menu-filter').css("display","none");
			$("div").find(".right-cnt-maxW").removeClass("right-cnt-maxW");
			
			$("div").find(".sub_breadcrumb").addClass("maxW_div");
			$("div").find(".shop-container").addClass("maxW_div");
			if ($(window).width() > 900) {
				$('#products_grid_before').removeClass('mCustomScrollbar').removeAttr('data-mcs-theme');
			}
	}
		
	//screen 900 to hide filter

	if ($(window).width() < 900) {
		$('.menu-filter').css("display","block");
		//$('#products_grid_before').css("display","none");
		$('.main_left_grid').css("cssText", "width: 100% !important;");
		$("#products_grid_before").removeClass("main_left_grid_before");
	}
	if( $(".css_editable_display").css('display') == 'block') {
		$('.view-as').css('display','none');
	}
})

$(window).load(function(){
	var filter_label = $('.main_left').parent().find('.view-as-div').css("margin-left","0px");
	var filter_label = $('.main_left').parent().find('label.view-label').addClass('filter-label-alignment');
})


