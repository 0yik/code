odoo.define('hilti_website_faq.hilti_website_faq', function (require) {
"use strict";

    var base = require('web_editor.base');
    var ajax = require('web.ajax');
    var utils = require('web.utils');
    var core = require('web.core');
    var config = require('web.config');
    var _t = core._t;
   
    
    $(".faq_search_input").on('keyup', function (e) {
        if (e.keyCode == 13) {
        	$('.faq_search').click()
        }
    });
    
//    $('.faq_search').on('click', function(){
//		ajax.jsonRpc("/search/faq", 'call', {'search': $('.faq_search_input').val()}).then(function (data) {
//			$('.child_faq').html(data['render_html'])
//    	});
//    })
    
    function toggleIcon(e) {
        $(e.target)
            .prev('.panel-heading')
            .find(".more-less")
            .toggleClass('fa-chevron-up fa-chevron-down');
    }
    $('.panel-group').on('hidden.bs.collapse', toggleIcon);
    $('.panel-group').on('shown.bs.collapse', toggleIcon);
    
    
})