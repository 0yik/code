$(document).ready(function(){
	
	if($('div').hasClass('oe_list'))
		{
		$("div").find(".main").addClass("main_list");
		$("div").find("#products_grid").addClass("main_listid");
		$("div").find("#products_grid_before").addClass("main_listid_grid_before");
		$("div").find(".right-cnt-maxW").addClass("right-cnt-maxW_list");
	//	$("div").find(".products-grid-main").removeClass("main_list_grid");
		$("div").find(".in-stock").addClass("in_stock_list");
		$("div").find(".warning").addClass("warning_list");
		$("div").find(".product-name-h5").addClass("product-name-h5_list");
		$("div").find(".product-des").addClass("product-des_list");
		$("div").find(".oe_subdescription").addClass("oe_subdescription_list")
		$(".menu-filter").unbind("click"); 
		$('.menu-filter').css("display","none");
		
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
		$('.main_listid').css("cssText", "width: 100% !important;");
		$("#products_grid_before").removeClass("main_listid_grid_before");
	}else{
		
	}
});

$(window).load(function(){
	var filter_label = $('.main_list').parent().find('.view-as-div').css("margin-left","0px");
	var filter_label = $('.main_list').parent().find('label.view-label').addClass('filter-label-alignment');
})

