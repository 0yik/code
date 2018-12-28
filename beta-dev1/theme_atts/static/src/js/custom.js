odoo.define('theme_atts.custom', function (require) {
"use strict";

var ajax = require('web.ajax');

$(function () {
    var clickwatch = (function(){
          var timer = 0;
          return function(callback, ms){
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
          };
    })();

    var datePickerOptions = {
        pickTime: false,
        icons : {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
        },
        format: 'MM/DD/YYYY',
    }
    $('#payment_deadline').datetimepicker(datePickerOptions);
    $('#individual_dob').datetimepicker(datePickerOptions);
    $('#training_date').datetimepicker(datePickerOptions);
    $('.delegate_date').datetimepicker(datePickerOptions);
    $('body').on('click',".add_more_field_delegate_button", function(){
        $('.delegate_date').datetimepicker(datePickerOptions);
        $('.div_nationality select').change(function(){
            if ($(this).val() == 'others') {
                $(this).parent().siblings('.div_country').removeClass('hidden');
            } else {
                $(this).parent().siblings('.div_country').addClass('hidden');
            }
        });
    })

    var table_tbody = $(".input_fields_delegate");
    var table_tr = $(".input_fields_delegate tr");
    var add_button = $(".add_more_field_delegate_button");
    $('[data-toggle="tooltip"]').tooltip();
    $(add_button).click(function(e){
        var cloned_tr = table_tr.clone().find('input').val('').prop("checked", false).end();
        $(table_tbody).append(cloned_tr);
    });

    $('.div_nationality select').change(function(){
        if ($(this).val() == 'others') {
            $('.div_country').removeClass('hidden');
        } else {
            $('.div_country').addClass('hidden');
        }
    });
    $('.dietary_request select[name=dietary_request]').change(function(){
        if ($(this).val() == 'others') {
            $('.dietary_request_comment').removeClass('hidden');
        } else {
            $('.dietary_request_comment').addClass('hidden');
            $('.dietary_request_comment').val('');
        }
    });

    $('.quick_search').on('change', "select[name='course_title']", function () {
        clickwatch(function() {
            if ($("#course_title").val()) {
                ajax.jsonRpc("/course/class_infos/" + $("#course_title").val(), 'call').then(
                    function(data) {
                        var selectClass = $("select[name='class_date']");
                        // dont reload classes at first loading (done in qweb)
                        if (selectClass.data('init')===1 || selectClass.find('option').length===1) {
                            if (data.classes.length) {
                                selectClass.html('');
                                _.each(data.classes, function(x) {
                                    var opt = $('<option>').text(x[1])
                                        .attr('value', x[0]);
                                    selectClass.append(opt);
                                });
                                selectClass.parent('div').show();
                            }
                            else {
                                selectClass.val('').parent('div').hide();
                            }
                            selectClass.data('init', 0);
                        }
                        else {
                            selectClass.data('init', 0);
                        }
                    }
                );
            }
        }, 500);
    });

    $('.signup_student_type input[name=student_type]').change(function(){
        if ($(this).val() == 'corporate') {
            $('.corporate_details').removeClass('hidden');
            $('.corporate_details input').attr('required', 'required');
        } else {
            $('.corporate_details').addClass('hidden');
            $('.corporate_details input').removeAttr('required');
        }
    });
});
$(window).on('load',function(){
    if ($('.course_registration.success').length != 0) {
        $('#course_registration').modal('show');
    }
});
});