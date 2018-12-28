odoo.define('online_school_enrollment', function (require) {
"use str0ct";

    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var snippet_animation = require('web_editor.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb;
    var l10n = _t.database.parameters;
    var datepickers_options = {
        startDate: moment({ y: 1900 }),
        endDate: moment().add(200, "y"),
        calendarWeeks: true,
        icons : {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
           },
        language : moment.locale(),
        format : time.strftime_to_moment_format(l10n.date_format),
    }
    $("#family_detail_related_student").change(function()
    {
        var value = $('#family_detail_related_student').val();
        if (value == 'selected')
        {
            $("#div_student_new_name").hide();
            $("#div_exist_student").hide();
        }
        if (value == 'new')
        {
            $("#div_student_new_name").show();
            $("#div_exist_student").hide();
        }
        if (value == 'exist')
        {
            $("#div_exist_student").show();
            $("#div_student_new_name").hide();
        }
    });

    $(".payment_selection_button").click(function(){
        $('#payment_selection').modal('show');
    });
    
    $('#dob').datetimepicker(datepickers_options);
    $('#previous_school_admission_date').datetimepicker(datepickers_options);
    $('#previous_school_exit_date').datetimepicker(datepickers_options);
    
    $('#eb_to_date').datetimepicker(datepickers_options);
    $('#eb_from_date').datetimepicker(datepickers_options);
    
    $("#dob").change(function()
    {
        var birth = new Date($('#dob').val());
        var today = new Date();
        var nowyear = today.getFullYear();
        var nowmonth = today.getMonth();
        var nowday = today.getDate();
        var birthyear = birth.getFullYear();
        var birthmonth = birth.getMonth();
        var birthday = birth.getDate();
        var age = nowyear - birthyear;
        var age_month = nowmonth - birthmonth;
        var age_day = nowday - birthday;
        if(age_month < 0 || (age_month == 0 && age_day <0)) {
            age = parseInt(age) -1;
        }
        $('#age').val(age)
    });
    
    $('#add_mew_line').click(function() {
        var total_line = parseInt($('#total_line').val()) + 1;
        $('#total_line').val(total_line);
        if (total_line >= 1)
        {
            var delete_button_hide = total_line - 1;
            $("#delete_new_line_"+delete_button_hide).hide();
        }
        $('#islamic_studies_highest_achievement_row').parent().append('<tr id="islamic_studies_highest_achievement_row" class="delete_last_line_row_'+total_line+'" name="islamic_studies_highest_achievement_row">\
            <td>\
                <input type="text" style="height:43px; width:350px;border-top:none;" class="form-control" name="eb_institution_'+total_line+'" id="eb_institution_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;border-top:none;" class="form-control" name="eb_from_date_'+total_line+'" id="eb_from_date_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;border-top:none;" class="form-control" name="eb_to_date_'+total_line+'" id="eb_to_date_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;border-top:none;" class="form-control name="eb_achievement_'+total_line+'" id="eb_achievement_'+total_line+'"/>\
            </td>\
            <td name="delete_new_line_'+total_line+'" id="delete_new_line_'+total_line+'" class="delete_last_line"><button type="button" class="delete_last_line btn btn-primary" name="delete_new_line_'+total_line+'" id="delete_new_line_'+total_line+'">Delete</button></td>\
        </tr>');
        $('#eb_from_date_'+total_line).datetimepicker(datepickers_options);
        $('#eb_to_date_'+total_line).datetimepicker(datepickers_options);
        $('.delete_last_line').click(function() {
            $('.delete_last_line_row_'+total_line).remove();
            if (total_line != 0)
            {
                var show_delete_button = total_line - 1;
                $("#delete_new_line_"+show_delete_button).show();
            }
        });
    });



    $( "#school_ids" ).change(function()
    {
        var formData = {
            'school_id' : this.value,
          };
        $.ajax({
            type        : 'POST',
            url         : '/filter_data',
            data        : formData,
            dataType    : 'json',
            success     : function(data)
            { 
                if (data['standard_ids'])
                {
                    $("#standard_ids").html('<option>Select Course</option>');
                    for ( i = 0; i<  data['standard_ids'].length; i++ )
                    {
                        $("#standard_ids").append("<option value='"+data['standard_ids'][i]['id']+"'>"+data['standard_ids'][i]['name']+"</option>");
                    }
                }
            }
        });
    });

    $("#submit_admission_register").click(function(){
        // birth date validation
        var birth = new Date($('#dob').val());
        var today = new Date();
        var nowyear = today.getFullYear();
        var nowmonth = today.getMonth();
        var nowday = today.getDate();
        var birthyear = birth.getFullYear();
        var birthmonth = birth.getMonth();
        var birthday = birth.getDate();
        var age = nowyear - birthyear;
        var age_month = nowmonth - birthmonth;
        var age_day = nowday - birthday;
        if(age_month < 0 || (age_month == 0 && age_day <0)) {
            age = parseInt(age) -1;
        }
        if ((age == 15 && age_month <= 0 && age_day <=0) || age < 15)
        {
            alert("Age should be greater than 15 years.!");
            return false
        }
        else
        {
            $('#age').val(age);
        }

    });
});