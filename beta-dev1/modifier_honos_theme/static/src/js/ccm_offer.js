odoo.define('modifier_honos_theme.ccm_offer', function(require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

$(document).ready(function() {

    if(!('.timer_design')) {
        console.error("DOM doesn't contain offer section.");
    } else {
        ajax.jsonRpc('/modifier_honos_theme/get_current_offer', [[]]).then(function(discount) {
            if (discount) {
                $('.left_timer_container').show();
                $('.right_timer_container').show();
                var $left_content = $('.left_content');
                $left_content.find('h3')[0].innerHTML = discount.title;
                $left_content.find('p')[0].innerHTML = discount.desc || '';
                $left_content.find('a')[0].href = discount.href;

                var $timer = $('#timer');
                var start = moment.utc(discount.start);
                var end = moment.utc(discount.end);
                var now = moment.utc();
                if (now.isBetween(start, end)) {
                    var duration = end.diff(now);
                    var timer;
                    timer = setInterval(function() {
                        timeBetweenDates();
                    }, 1000);

                    function timeBetweenDates() {
                        now = moment.utc();
                        duration = moment.duration(end.diff(now));
                        if (duration.asSeconds() <= 0) {
                            clearInterval(timer);
                        } else {
                            $("#days").text(duration.days());
                            $("#hours").text(duration.hours());
                            $("#minutes").text(duration.minutes());
                            $("#seconds").text(duration.seconds());
                        }
                    }
                }

                var $timer_sale_icon = $('.timer_sale_icon');
                $timer_sale_icon[0].innerHTML = discount.disc + '%' + '<span>off</span>';

                // change image
                var $right_timer_container = $('.right_timer_container');
                var img_url = '/web/image/website.discount/' + discount.id + '/image';
                $right_timer_container[0].style = "background-image:url('"+ img_url +"')";
            } else {
                $('.left_timer_container').hide();
                $('.right_timer_container').hide();
            }
        });
    }
});

});
