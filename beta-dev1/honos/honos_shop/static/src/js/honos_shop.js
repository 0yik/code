$(document).ready(function(){ 
	//Push toggle for filter option
	$('.menu-filter').click(function(){
		$("#products_grid_before").css({"width":"300px","transition":"0.5s","padding-left":"2%"});
		$("#wrapwrap").css({"margin-left":"300px","transition":"0.5s"});
		$('body').css("overflow-x","hidden");
		$(".transparent").css("display","block");
	});
	$('.mobile-view-filter-close-btn').click(function(){
		$("#products_grid_before").css({"width":"0px","transition":"0.5s","padding-left":"0%"});
		$("#wrapwrap").css({"margin-left":"0px","transition":"0.5s"});
		$(".transparent").css("display","none");
	});
	
	//Show clear all link when any attribute is selected on load
	$("form.js_attributes input:checked").each(function(){ 
		var self=$(this)
		//For Color
		var curr_parent=self.parent().closest("li").find(".attribute-filter-div"); 
		var clear_link = curr_parent.find("a.clear-all-variant");
		//For Checkbox
		var parent_for_checkbox = self.closest("ul").closest("li").find(".attribute-filter-div").find("a.clear-all-variant");
		clear_link.css("display","block");
		parent_for_checkbox.css("display","block");
	});
	
	/* on clicking at any portion of document the filter section will be closed*/
	$(document).mouseup(function (e){
	    var container = $("#products_grid_before");
	    if (!container.is(e.target) && container.has(e.target).length === 0){
	    	if( $("#products_grid_before").css('width') == '300px') {
				$("#products_grid_before").css({"width":"0px","transition":"0.5s","padding-left":"0%"});
				$("#wrapwrap").css({"margin-left":"0px","transition":"0.5s"});
				$(".transparent").css("display","none");
			}		    
	    }
	});
	
	if($(window).width() < 900) {
		$("#products_grid_before").removeClass("main_left_grid_before");
		$("#products_grid_before").removeClass("main_right_grid_before");
		$("#products_grid_before").removeClass("main_listid_grid_before");
	}
	
	// Breadcrumb in category page
	$( ".products_category_ul li" ).each(function() {
		var current_li= $(this);
		if ( current_li.hasClass( "active" ) ) {
			/*var c = current_li.find("a:first-child");*/
			var c = current_li.find("a");
			if(c.html() == "All Products"){
				$(".select-nevigation-home").html("Home");
			}
			else{
				$(".select-nevigation-home").html("Home");
				$(".select-nevigation-span").html("/");
				$(".select-nevigation-child").html(c.html());
			}
	    }
	});
	
	// Show clear all link when any attribute is selected
	var $new_class_variant = $(".clear-all-variant")
	if($new_class_variant){
		$(".clear-all-variant").click(function(){
			var self=$(this)
			var curent_div = $(self).closest("li");
			$(curent_div).find("input:checked").each(function(){
				$(this).removeAttr("checked");
			});
			$("form.js_attributes input").closest("form").submit();
		});
	}
	
	/* changing the sequence of clikcked checkbox of attribute to first level*/
	$("form.js_attributes input:checked").each(function(){ 
		var self=$(this)        	
		var curr_parent=self.closest("li");        	
		var curr_att=curr_parent.closest("ul").find("li").first(); 
		$(curr_att).before(curr_parent);
		
		var curr_parent_color=self.closest("div");        	
		var curr_att_color=curr_parent.closest("li").find("div.color-div").first(); 
		$(curr_att_color).before(curr_parent_color);
	});
	
	//Added Custom Scrollbar Js
	if($(window).width() > 1000)
	{
		var script=document.createElement('script');
	    script.type='text/javascript';
	    script.src="/honos_shop/static/src/js/jquery.mCustomScrollbar.concat.min.js";
	    $("head").append(script);
	}
	// for show tab
	var p_c=$(".p_Count").attr("data-id");
	if(p_c<20)
	{  
		$(".filter-show").addClass("show_inactive")
	}
	$(".ppg_show").click(function()
	{
		var show_ppg=$(this).attr("data-id");
		var url =document.URL
		if((url.indexOf("ppg=16") >= 0))
		{
				var url = url.replace("ppg=16", "");
		}
		else if((url.indexOf("ppg=20") >= 0))
		{
				var url = url.replace("ppg=20", "");
		}
		if (url.indexOf('?') == -1)
			window.location.href = url+"?ppg="+show_ppg;
		if (!(url.indexOf('?') == -1))
			window.location.href = url+"&ppg="+show_ppg;
	});
});


