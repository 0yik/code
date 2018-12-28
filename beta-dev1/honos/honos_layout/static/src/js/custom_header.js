(function($){
$(window).load(function(){
	$(".menu_1_column_div").mCustomScrollbar({
		scrollButtons: {
	enable: true
	},
	theme: "dark",
	horizontalScroll: true,
	advanced: { updateOnContentResize: true, updateOnBrowserResize: true }
	}); 
	});
})(jQuery);

$(window).resize(function () {
	if ($(window).width() > 1201) {
		$('.first-level-category-image').addClass("active-li");
		// Header Stick
		var login_class = $('#oe_main_menu_navbar');
		var navbarheight = $('#oe_main_menu_navbar').height();
		var rightBox = $('.navbar-top-collapse');
		if($(".navbar-top-collapse").length > 0)
		{
			var x = rightBox.offset();
			var navPos = x.top;
			if(login_class)
			{
				$(window).scroll(function() {
					var scrollPosition = $(this).scrollTop();
					if (scrollPosition >= navPos) {
						rightBox.addClass("header-stick");
						rightBox.css("top", + navbarheight);
						rightBox.css({"margin-top":"0px"});
						$('.navbar-brand img').addClass("logo-stick");
						$('.navbar-brand img').css("top", + navbarheight);
					} else {
						rightBox.removeClass("header-stick");
						$('.navbar-brand img').removeClass("logo-stick");
						rightBox.css({"margin-top":"10px"});
					}
				});
			}else{
				rightBox.css({"top": "0"});
			}
		}
		
		
		
		
		
	}else if($(window).width() < 1200){
		$(window).scroll(function() {
			$('div').removeClass("header-stick");
		})
		$('.first-level-category-image').removeClass("active-li");
	}
});	

$(document).ready(function(){ 
	
	
/*================= Category-Function-For-Style-4 ======================*/
	
	$.fn.change_categ_sty_4 = function(){
		
		if($(this).find('div , ul').hasClass("style_4_toggel_div")){
	
				$(this).find('.style_4_menu_list').each(function(){
					var all_li = $(this).find('li');

					var dynamic_href = '';
					
					$(this).mouseenter(function(){
						dynamic_href = $(this).parent().find('.style_4_menu_name').attr('href');
						$(this).find('.see_more').attr("href",dynamic_href);
					});
					
					$(all_li).each(function(i){
						if(i<=3){
							$(this).show();
						}else{
							$(this).hide();
						}
					});
					$(this).append("<a class='see_more' href='"+dynamic_href+"'>See More...</a>");
					
				});
			
		}

	}
	
	
	
	
	if ($(window).width() > 1200) {
		
		/****************** Style-4-mega-menu ******************/
		$('#top_menu > li').mouseenter(function(){
			$(this).change_categ_sty_4();
		});
		$('#top_menu > li').mouseleave(function(){
			$(this).find('.style_4_menu_list').each(function(){
				$(this).find('.see_more').remove();
			})
		});
		/*******************************************************/
		
		/****************** Style-2-mega-menu ******************/
		$("#top_menu > li > a").hover(function(){
					
			if($(this).parent().find('div , ul').hasClass("style_2_toggel_div")){
				
				/*-=-=--=-=-=-=-=-=-=- List-Hover -=-=-=-=-=-=-=-=-=-=-=-*/
				
				$(".menu_name").mouseenter(function(){
					
					var curr_id = $(this).closest("li").attr("id")
					
					$(".style_2_toggel_div").find(".categ_li").find(".fa-caret-right").css('visibility','visible')
					
					$(".categ_li").find('.menu_name').css({
						'border-style': 'none solid solid none',
						'border-width': '1px',
						'border-color': '#ddd'
					})
					
					$(this).css({
						'border-style': 'none none solid none',
						'border-width': '1px',
						'border-color': '#ddd'
					})
					$(".style_2_toggel_div").find(".categ_li[id='"+ curr_id +"']").find(".fa-caret-right").css('visibility','hidden')
					
					$(".style_2_toggel_div").find(".open_right_div").css('display','none')
					$(".open_right_div").css('background', 'url(/style_2/static/src/img/' + curr_id + '.png) no-repeat right')
					$(".style_2_toggel_div").find(".open_right_div[id='"+ curr_id +"']").css('display','block')
				});
				
				if($(window).width() < 1200){
					
					/************* Menu-Hover **************/
					
					$('#top_menu > li > a').on('click touchend');
					
					$("#top_menu > li > a").hover(function(){
						
						$(".style_2_toggel_div").css({
							'display':'none',
							'animation':'unset',
							'top':'0',
							'left':'0',
							'position':'relative'
						})
					});	
					
					$("#top_menu > li > a").click(function(){
						
						$(".style_2_toggel_div").css('display','block');
						
						/*********************** List-Hover ************************/
						
						$(".categ_li").mouseenter(function(){
							
							var curr_id = $(this).closest("li").attr("id")
							$(".categ_li").find('.menu_name').css('border','1px solid #ddd');
							
							$(this).find('.menu_name').css({
								'border-style': 'solid solid none solid',
								'border-width': '1px',
								'border-color': '#ddd'
							})
							$(".style_2_toggel_div").find(".categ_li[id='"+ curr_id +"']").find(".fa-caret-right").css('visibility','hidden')
							
							$(".style_2_toggel_div").find(".open_right_div").css('display','none')
							$(".open_right_div").css('background', 'url(/style_2/static/src/img/' + curr_id + '.png) no-repeat right')
							$(".style_2_toggel_div").find(".open_right_div[id='"+ curr_id +"']").css('display','block')
							
						});
						
					});
					
					/***************** Default-(Sign-In)-CSS *******************/
					
					$("#top_menu").find("a[href='/web/login']").closest("li").css({
						'display':'inline-block',
						'width':'100%'
					});
				}
				
				if($(window).width() < 370){
					
					$('.categ_li').css('width','100%');
					
					$("#top_menu > li > a").click(function(){
						
						$(".categ_li").unbind('mouseenter');
						$(".style_2_toggel_div").css('height','unset')
						$(".style_2_toggel_div").find(".fa-caret-right").css('visibility','hidden');
						$(".style_2_toggel_div").find(".menu_name").css('border','1px solid #ddd');
						
					});
					
					$(".categ_li").click(function(){
						
						var curr_id = $(this).attr("id")
						
						/***************** Plus-Minus-Logic *******************/
						
						$(".open_right_div").css({
							'background':'unset',
							'position':'unset'
						})
						
						if ($(".style_2_toggel_div").find(".open_right_div[id='"+ curr_id +"']").css('display') == 'none') {
							
							$(".style_2_toggel_div").find(".open_right_div").css('display','none');
							$(".style_2_toggel_div").find(".categ_li").find('.menu_name i').removeClass('fa-minus')
							$(".style_2_toggel_div").find(".categ_li").find('.menu_name i').addClass('fa-plus')
							$(".style_2_toggel_div").find(".categ_li[id='"+ curr_id +"']").find('.menu_name i').addClass('fa-minus')
							$(".style_2_toggel_div").find(".open_right_div[id='"+ curr_id +"']").slideDown(200);
							
						}else{
							$(".style_2_toggel_div").find(".categ_li[id='"+ curr_id +"']").find('.menu_name i').removeClass('fa-minus')
							$(".style_2_toggel_div").find(".categ_li[id='"+ curr_id +"']").find('.menu_name i').addClass('fa-plus')
							$(".style_2_toggel_div").find(".open_right_div[id='"+ curr_id +"']").slideUp(200);
						}

					});
				
				}
				
			}
			
			
		});
		/*******************************************************/
		
		$('#top_menu > li > a').mouseenter(function(){
			
			$(this).addClass("active_menu_a");
			if ($(this).parent().find('div , ul').hasClass('custom-menu-inside-div')){
				$(this).parent().find('.custom-menu-inside-div').css("display","block");
				var first_li = $('.first-level-category-li').first('li');
				first_li.find('.first-level-category-image').addClass('active-li');
				first_li.find('.toggel_div').find('.menu_1_div').css("display","block");
				first_li.find('.toggel_div').css("display","block");
			}
			else{
				$(this).next('ul').css("display","block");
			}
		});
		$('#top_menu > li > a').mouseleave(function(){
			$(this).removeClass("active_menu_a");
			if ($(this).parent().find('div , ul').hasClass('custom-menu-inside-div')){
				$(this).parent().find('.custom-menu-inside-div').css("display","none");
			}
			else{
				$(this).next('ul').css("display","none");
			}
		});
		$('.custom-menu-inside-div, #top_menu > li > a + ul').mouseenter(function(){
				$(this).parent().find("a").first().addClass("active_menu_a");
				$(this).css("display","block");
		});
		$('.custom-menu-inside-div, #top_menu > li > a + ul').mouseleave(function(){
			$(this).css("display","none");
			$('#top_menu > li > a').removeClass("active_menu_a");
		});
		
		// Dynamic category hover
		$('.first-level-category-li').mouseenter(function(){
			var self =$(this) 
			var first_div = $(self).find('.first-level-category-image');
			first_div.addClass("active-li");
			self.find('.toggel_div').css("display","block");
			self.find('.toggel_div').find('.menu_1_div').css("display","block");
		});
		$('.first-level-category-li').mouseleave(function(){
			var self =$(this)
			var first_div = $(self).find('.first-level-category-image')
			first_div.removeClass("active-li");
			self.find('.toggel_div').find('.menu_1_div').css("display","none");
			self.find('.toggel_div').css("display","none");
		});
		
		//active first category
		$('.first-level-category').mouseleave(function(){
			var first_li = $('.first-level-category-li').first('li').find('.first-level-category-image').addClass('active-li');
			first_li.next('.toggel_div').find('.menu_1_div').css("display","block");
			first_li.next('.toggel_div').css("display","block");
		});
		
		$('.custom-menu-inside-div').addClass('block-none');
		$('.mobile-view-static-menu').css("display","none");
		//$('.top-custom-menu').removeClass("dropdown");
		$('.fisrt_li').addClass('first-level-category');
		$('.fisrt_li').removeClass('category-mobile-view');
		$('.first-level-li ').find('ul.sub_menu').removeClass('second_level-ul dropdown-menu');
		$('.sub-menu-ul-heading ').find('ul.third-level-ul').addClass('dropdown-menu');
		$('.category-heading-div').removeClass('dropdown-submenu');
		$('.expand-div').removeClass('dropdown-submenu');
		$('.submenu-a').removeClass('fa fa-chevron-right');
		$('.sub_menu').removeClass('dropdown-menu');
		$('.third-level-ul').removeClass('dropdown-menu');
    		

		// Header Stick
		var login_class = $('#oe_main_menu_navbar');
		var navbarheight = $('#oe_main_menu_navbar').height();
		var rightBox = $('.navbar-top-collapse');
		if($(".navbar-top-collapse").length > 0)
		{
		var x = rightBox.offset();
		var navPos = x.top;
		if(login_class)
		{
			$(window).scroll(function() {
				var scrollPosition = $(this).scrollTop();
				if (scrollPosition >= navPos) {
					rightBox.addClass("header-stick");
					rightBox.css("top", + navbarheight);
					rightBox.css({"margin-top":"0px"});
					$('.navbar-brand img').addClass("logo-stick");
					$('.navbar-brand img').css("top", + navbarheight);
				} else {
					rightBox.removeClass("header-stick");
					$('.navbar-brand img').removeClass("logo-stick");
					rightBox.css({"margin-top":"10px"});
				}
			});
		}else{
			rightBox.css({"top": "0"});
		}
	}
}
	else{
		$('.category-mobile-view').removeClass('first-level-category');
		$('.first-level-li ').find('ul.sub_menu').addClass('second_level-ul dropdown-menu');
		$('.sub-menu-ul-heading ').find('ul.third-level-ul').addClass('dropdown-menu');
		$('.category-heading-div').addClass('dropdown-submenu');
		$('.expand-div').addClass('dropdown-submenu');
		$('.fisrt_li').removeClass('first-level-category');
		$('.fisrt_li').addClass('category-mobile-view');
		$('.submenu-a').addClass('fa fa-chevron-right');
		$('.first-level-left-div').removeClass('first-level-left-div');
		$('.toggel_div').removeClass('toggel_div');
		$('.menu_expand').removeClass('menu_1_div');
		$('.menu_expand_overflow').removeClass('menu_1_column_div');
		$('.second_level-ul').removeClass('sub_menu');
		$('.toggel-div-effect').addClass('dropdown-menu').css("position","unset");
		$('.submenu_expand').removeClass('dropdown-menu second_level-ul');
		$('.first-level-category-a').removeClass('dropdown-toggle').removeAttr("data-toggle", "dropdown");
		$('.second-level-a').removeClass('dropdown-toggle').removeAttr("data-toggle", "dropdown");
		$('.sub_menu_list').removeClass('dropdown-toggle').removeAttr("data-toggle", "dropdown");
		$('.first-level-category-image').removeClass("active-li");
		
		
		var dynamic_menu_li = $('ul.custom-menu-inside-div').parent();
		dynamic_menu_li.addClass("dropdown");
		dynamic_menu_li.find('a').first().addClass("dropdown-toggle");
		dynamic_menu_li.find('a').first().attr("data-toggle", "dropdown");
	}
	
	
	
/*	//Search Icon 
	$('.search_link').click(function(){
			$("#wrapwrap").css({"transition":"0.5s ease-out"});
			$(".main-header-maxW").addClass("transparentbg");
			$(".honos_close").css("display","block");
			$(".anim-search").css("display","block");
			$(".main-header-left").css("display","none");
			$(".offer-center").css("display","none");
			$(".company-phone-div").css("display","none");
			$("body").addClass("scroll_remove");
			
			var animDuration = 500;
		
			$(".anim-search").addClass("zoom-animation");
		    setTimeout(function(){
		    	$(".anim-search").removeClass("zoom-animation");
		    }, animDuration
		);
	});*/
	
	//First Static Menu in header
	$(".cat-column").mouseenter(function(){
		var self = $(this);
		self.addClass('opacity-full');
		var button_cat = $(self).find('a.button_cat');
		button_cat.addClass('menu-cate-hover');
		$('.cat-column').addClass('opacity');
	});
	
	$(".cat-column").mouseleave(function(){
		var self = $(this);
		var button_cat = $(self).find('a.button_cat');
		button_cat.removeClass('menu-cate-hover');
		$('.cat-column').removeClass('opacity');
		self.removeClass('opacity-full');
	});
	//third static menu in header
	$(".ctg_name_img_container").mouseenter(function(){
		var self = $(this);
		self.addClass('opacity-full');
		$(".ctg_name_img_container").addClass('opacity');
	});
	$(".ctg_name_img_container").mouseleave(function(){
		var self = $(this);
		$('.ctg_name_img_container').removeClass('opacity');
		self.removeClass('opacity-full');
	});
	
	
	//Scroll up 
	$(window).scroll(function(){
		if ($(this).scrollTop() > 300) {
			$('.scrollup-div').fadeIn();
		} else {
			$('.scrollup-div').fadeOut();
		}
	}); 

	$('.scrollup-div').click(function(){
		$("html, body").animate({ scrollTop: 0 }, 1000);
	});
	
	// Dropdown manu
	$('.dropdown-submenu span.submenu-a').on("click", function(e){
		$(this).next('ul').toggle();
		$(this).next('div.toggel-div-effect').toggle();
		e.stopPropagation();
		e.preventDefault();
		
		var clicks = $(this).data('clicks');
		  if (clicks) {
			 $(this).removeClass("fa-chevron-down").addClass("fa-chevron-right");
		  } else {
			 $(this).removeClass("fa-chevron-right").addClass("fa-chevron-down");
		  }
		  $(this).data("clicks", !clicks);
	});
	/*Remove a Sub-menu Html Field Empty Div*/	
	$('.custom-menu-inside-div').each(function(){		
	if ($(this).length && $(this).text().trim().length == 0 ){			
		$(this).remove();		
		}	
	});
	
	$('#top_menu li:has("ul.custom-menu-inside-div")').addClass("dropdown");
	$('#top_menu li:has("ul.custom-menu-inside-div")').find("a:first").addClass("dropdown-toggle");
	$('#top_menu li:has("ul.custom-menu-inside-div")').find("a:first").attr("data-toggle", "dropdown");
	$('#top_menu li:has("div.custom-menu-inside-div")').addClass("dropdown");
	$('#top_menu li:has("div.custom-menu-inside-div")').find("a:first").addClass("dropdown-toggle");
	$('#top_menu li:has("div.custom-menu-inside-div")').find("a:first").attr("data-toggle", "dropdown");
	
});

// Show first category by default on load the window
$(window).load(function(){
	var first_li = $('.first-level-category-li').first('li');
	first_li.find('.first-level-category-image').addClass('active-li');
	first_li.find('.toggel_div').find('.menu_1_div').css("display","block");
	first_li.find('.toggel_div').css("display","block");
	if($('.dynamic_active_inactive')){
		$('.dynamic_active_inactive').parent().find("div.block-none").css("display","none");
	}
})




//for searching
$(document).keyup(function(e) {
    if (e.which == 27) {
    	$('body').css('position','relative')
        $(".main-header-maxW").removeClass("transparentbg");
    	$(".honos_close").css("display","none");
    	$(".anim-search").css("display","none");
    	$(".main-header-left").css("display","block");
    	//$(".offer-center").css("display","block");
    	$(".company-phone-div").css("display","block");
    	$("body").removeClass("scroll_remove");
    }
});






/********************************************** Style-3-Mega-Menu-JS ********************************************************/

/*$(document).ready(function(){

	if($(window).width() < 1200){
		
		$('.style_3_menu_item').hover(function(){
			
			$(".style_3_toggel_div").css({
				'display':'none',
				'animation':'unset',
				'top':'0',
				'left':'20px',
				'position':'relative'
			});
		});
		
		$('.style_3_menu_item').click(function(){
			
			$('.style_3_right_img_main').css('display','none')
			$('.style_3_main_wrap').css('width','100%')
			
			if ($(".style_3_toggel_div").css('display') == 'none') {
			
				$(".style_3_toggel_div").css('display','block');
				
			}else{
				$(".style_3_toggel_div").css('display','none');
			}
		});
		
	}
	
	if($(window).width() < 800){
		
		$('.style_3_menu_item').on('click touchend');
		
		if(e.type === 'touchstart'){
			alert('touch')
		}else{
			alert('no-touch')
		}
		
			$('.style_3_menu_item').hover(function(){
				
				$(".style_3_toggel_div").css({
					'width':'90%',
					'margin': '0 auto'
				});
				
			});
	}
	
	if($(window).width() < 750){
		
		$('.navbar-toggle').click(function(){
			$('.style_3_menu_item').unbind('hover');
		});

	}
	
});*/
/********************************************** Style-2-Mega-Menu-JS ********************************************************/

