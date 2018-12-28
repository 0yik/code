$('document').ready(function(){
    var boxWidth = $(".right_top").height();
    var bottombox = $(".right_bottom").height();
    var topim = $(".rtop_image_img").height();
    var botim = $(".rbot_image_img").height();
    console.log("Sssssss",bottombox);
    // $('.front_left').click(function(e){
    // 	$('.front_left').addClass('full_width');
    // 	$(".front_right").addClass('hidden');
    // 	$(".video_block").removeClass('hidden');
    // 	$(this).addClass('hidden');
    // });

    // $('.video_block .fa-times, .video_block #small_logo').click(function(e){
    // 	$('.front_left').removeClass('full_width');
    // 	// window.reload()
    // 	$(".front_right").removeClass('hidden');
    // 	$(".video_block").addClass('hidden');
    // 	$(".front_left").removeClass('hidden');
    // 	$(this).parent().addClass('hidden');
    // });
    window.onload = setTimeout(function(){document.body.setAttribute("class", document.body.getAttribute('class') + " loaded");}),10000)

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
        // $(".front_right").addClass('hidden');
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
});
