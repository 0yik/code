odoo.define('compare.compare_product', function(require) {
	"use strict";
	var base = require('web_editor.base');
	var ajax = require('web.ajax');
	var utils = require('web.utils');
	var core = require('web.core');
	
	var _t = core._t;
	var product_count
	
	function getcompareproduct()
	{
		
		ajax.jsonRpc('/compare_product', 'call', {}).then(function(data) 
		{
			if(data.productids.length==0)
			{
				$(".product_count").css("display","none")
				$(".apply-compare").css("display","none")
			}
			else
			{
				$(".product_count").css("display","inline-block")
				$(".apply-compare").css("display","block")
			}
			
		product_count=data.productids.length
		$('.product_count').html(product_count)
		
		if(product_count > 1){
			$('.compare_product_count').html("(<span class='product_count'> "+product_count+" </span>items)")
		}
		else if(product_count == 1){
			$('.compare_product_count').html("(<span class='product_count'> "+product_count+" </span>item)")
		}		
		for (var j = 0; j < data.productids.length; j++) 
		{
			var pid = data.productids[j]
			$(".add2compare[data-id='" + pid + "']").attr("checked",true)
			$(".add2compare[data-id='" + pid + "']").attr("disabled", true)
			$("i[data-id='" + pid + "']").addClass("theme_color_class")
			
		}
		}).fail(function(e)
				{
			$(".comparelist_error").html("May something goes wrong , Try after some time ...");
			$(".comparelist_error").css("display","block");
			setTimeout(function(){
				$(".comparelist_error").css("display","None");
			},2000)
			$('.cus_theme_loader_layout').addClass('hidden')
		});
	}
	
	
	function getcompare(pid,status)
	{	
		var pid=pid;
		var chk_status=status;
		ajax.jsonRpc('/compare_product', 'call', {'product_id' : pid,'status':true}).then(function(data) {
			console.log(data)
			if(data.productids.length==0)
			{
				$(".product_count").css("display","none")
				$(".apply-compare").css("display","none")
			}
			else
			{
				$(".product_count").css("display","inline-block")
				$(".apply-compare").css("display","block")
			}
			
			product_count=data.productids.length
			$('.product_count').html(product_count)
			
			if(data.productallow==false)
				{

					$(".comparelist_error").html("You can Not comaper Different Category's Product !!!");
					$(".comparelist_error").css("display","block");
					setTimeout(function(){
						 $(".comparelist_error").css("display","None");
						 $(".comparelist_error").html("");
					},5000)
				}
			else
				{
					$(".comparelist_error").html("Product Added");
					$(".comparelist_error").css("display","block");
					setTimeout(function(){
						$(".comparelist_error").css("display","None");
						 $(".comparelist_error").html("");
					},5000)
				}
			for (var j = 0; j < data.productids.length; j++) 
			{
				var pid = data.productids[j]
				$(".add2compare[data-id='" + pid + "']").attr("checked",true)
				$(".add2compare[data-id='" + pid + "']").attr("disabled", true)
				$("i[data-id='" + pid + "']").addClass("theme_color_class")
				
			}
			
		}).fail(function(e)
				{
			$(".comparelist_error").html("May something goes wrong , Try after some time ...");
			$(".comparelist_error").css("display","block");
			setTimeout(function(){
				$(".comparelist_error").css("display","None");
			},2000)
			$('.cus_theme_loader_layout').addClass('hidden')
		});
	}
		
	
	$(".apply-compare").click(function()
	{	
		$('.cus_theme_loader_layout').removeClass('hidden'); 
		
		ajax.jsonRpc('/compare_products_popout', 'call', {}).then(function(data)
		{
			$(".common-continer").html(data);
			$(".common-main-div").css("display","block").addClass("zoom-fadein");
			$('.cus_theme_loader_layout').addClass('hidden');	
		})
		
	});
	
	$(".common-close-btn").click(function(){
		$(".common-continer").html("");
		$(".common-main-div").css("display","none");
	})
	
	$(document).on( 'keydown', function(e){
		if(e.keyCode === 27) {
			$(".common-continer").html("");
			$(".common-main-div").css("display","none");
		}
	});
		
	getcompareproduct()
	
	$(".add2compare").change(function() 
	{
		var chk_status="";
		if(this.checked)
			chk_status=true
		var pid = $(this).attr('data-id');
		getcompare(pid,chk_status)
	});
	
	$(".remove2compare").click(function() 
	{
				var pid = $(this).attr('data-id');
				var self = $(this).parent().parent();
				self.css('display', 'none');
				$(".product[data-id='" + pid + "']").css("display","none")
				product_count=product_count-1
				$('.product_count').html(product_count)
				
				if(product_count > 1){
					$('.compare_product_count').html("(<span class='product_count'> "+product_count+" </span>items)")
				}
				else if(product_count == 1){
					$('.compare_product_count').html("(<span class='product_count'> "+product_count+" </span>item)")
				}
				
				ajax.jsonRpc('/compare_product', 'call', {'product_id' : pid,'status':false	}).then(function(data) 
				{
					console.log(data);
					if(product_count==0)
					{
					location.reload();
					}
				})
				
				if(product_count <=3){
					$('.compare_product_heading_right_div .bx-next').css('display','none');
					$('.compare_product_heading_right_div .bx-prev').css('display','none');
				}
				
	})
	return {
		getcompare:getcompare,
		getcompareproduct:getcompareproduct
	};
})



$(window).load(function(){
	
	if ($(window).width() > 1100) {
		var slider = $('.bxslider_compare').bxSlider({
			slideWidth: 300,
			minSlides: 3,
			maxSlides: 3,
			slideMargin: 10,
			auto: false,
			infiniteLoop: false,
			pager:false,
		})
	}else if ($(window).width() < 800){
		var slider = $('.bxslider_compare').bxSlider({
			slideWidth: 350,
			minSlides: 1,
			maxSlides: 1,
			slideMargin: 10,
			auto: false,
			infiniteLoop: false,
		})
	}else{
		var slider = $('.bxslider_compare').bxSlider({
			slideWidth: 300,
			minSlides: 2,
			maxSlides: 2,
			slideMargin: 10,
			auto: false,
			infiniteLoop: false,
		})
	}
	
	var compare_product_img = $('.compare_product_img').height();
	var compare_product_name = $('.compare_product_name').height();
	var compare_product_price = $('.compare_product_price').height();
	var compare_product_availability = $('.compare_product_availability').height();
	var compare_product_description = $('.compare_product_description').height();
	var compare_product_rating = $('.compare_product_rating').height();
	var compare_product_variant = $('.compare_product_variant').height();
	var compare_product_sku = $('.compare_product_sku').height();
	var compare_product_image_td = $('.compare_product_div').height();
	
	var total_height = compare_product_variant + compare_product_rating + compare_product_description + compare_product_img + compare_product_name + compare_product_price + compare_product_availability
	$('.blank_div').css('height',total_height);
	
	
});

