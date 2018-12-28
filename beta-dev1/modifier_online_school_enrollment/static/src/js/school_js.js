odoo.define('modifier_online_school_enrollment', function (require) {
"use str0ct";

    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var Model = require('web.Model');
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

    $("#first_name").keypress(function (e)
    {
        $("#full_name_errmsg").hide();
    });
    $("#nric").keypress(function (e)
    {
        $("#nric_errmsg").hide();
    });
    $("#address1").keypress(function (e)
    {
        $("#address1_errmsg").hide();
    });
    $("#address2").keypress(function (e)
    {
        $("#address2_errmsg").hide();
    });
    $("#hp_no").keypress(function (e)
    {
        $("#hp_no_errmsg").hide();
    });
    $("#email").keypress(function (e)
    {
        $("#email_errmsg").hide();
    });
    $("#phone_no").keypress(function (e)
    {
        $("#phone_no_errmsg").hide();
        $('#general_tab').css('background-color','#fff');
    });
    $("#mobile_no").keypress(function (e)
    {
        $("#mobile_no_errmsg").hide();
        $('#general_tab').css('background-color','#fff');
    });
    $("#occupation").keypress(function (e)
    {
        $("#occupation_errmsg").hide();
    });
    $("#income").change(function()
    {
        $("#income_errmsg").hide();
    });
    $("#standard_ids").change(function()
    {
        $("#standard_ids_errmsg").hide();
    });
    $("#year_ids").change(function()
    {
        $("#year_ids_errmsg").hide();
    });
    $("#general_survey_id").change(function()
    {
        $("#general_survey_id_errmsg").hide();
        $('#general_survey_tab').css('background-color','#fff');
    });
    $("#highest_qualification_id").change(function()
    {
        $("#highest_qualification_id_errmsg").hide();
        $('#education_background_tab').css('background-color','#fff');
    });
    $("#eb_institution").keypress(function (e)
    {
        $("#eb_institution_errmsg").hide();
        $('#education_background_tab').css('background-color','#fff');
    });
    $("#eb_from_date").keypress(function (e)
    {
        $("#eb_institution_errmsg").hide();
        $('#education_background_tab').css('background-color','#fff');
    });
    $("#eb_to_date").keypress(function (e)
    {
        $("#eb_institution_errmsg").hide();
        $('#education_background_tab').css('background-color','#fff');
    });
    $("#eb_achievement").keypress(function (e)
    {
        $("#eb_institution_errmsg").hide();
        $('#education_background_tab').css('background-color','#fff');
    });

    $(".payment_selection_button").click(function(){
        if ($('#first_checkbox').is(':checked') == false)
        {
            alert('Please select all checkbox');
            return false
        }
        if ($('#second_checkbox').is(":checked") == false)
        {
            alert('Please select all checkbox');
            return false
        }
        if ($('#third_checkbox').is(":checked") == false)
        {
            alert('Please select all checkbox');
            return false
        }
        $('#declaration_form').modal('hide');
        $('#payment_selection').modal('show');
    });

    $(".open_declaration_form_button_new").click(function(){
        // date of birth
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

        var full_name = document.getElementById("first_name").value
        var nric = document.getElementById("nric").value
        var email = document.getElementById("email").value
        var address1 = document.getElementById("address1").value
        var address2 = document.getElementById("address2").value
        var hp_no = document.getElementById("hp_no").value
        var occupation = document.getElementById("occupation").value
        var income = document.getElementById("income").value
        var highest_qualification = document.getElementById("highest_qualification_id").value
        var phone_no = document.getElementById("phone_no").value
        var mobile_no = document.getElementById("mobile_no").value
        var select_school = document.getElementById("school_ids").value
        var select_courses = document.getElementById("standard_ids").value
        var select_intake = document.getElementById("year_ids").value
        var general_survey_val = document.getElementById("general_survey_id").value
        // var eb_institution_val = document.getElementById("eb_institution").value
        // var eb_from_date_val = $('#eb_from_date').val()
        // var eb_to_date_val = $('#eb_to_date').val()
        // var eb_achievement_val = $('#eb_achievement').val()
        
        if (full_name == '')
        {
            document.getElementById("first_name").focus();
            $("#full_name_errmsg").html("Please Enter Full Name").show();
            return false
        }
        if (address1 == '')
        {
            document.getElementById("address1").focus();
            $("#address1_errmsg").html("Please Enter Block").show();
            return false
        }
        if (address2 == '')
        {
            document.getElementById("address2").focus();
            $("#address2_errmsg").html("Please Enter Street").show();
            return false
        }
        // Date Of birth
        if ($('#dob').val() == '')
        {
            $('#dob').focus();
            return false
        }
        if (nric == '')
        {
            document.getElementById("nric").focus();
            $("#nric_errmsg").html("Please Enter Nric").show();
            return false
        }
        if (hp_no == '')
        {
            document.getElementById("hp_no").focus();
            $("#hp_no_errmsg").html("Please Enter HP NO").show();
            return false
        }
        if (occupation == '')
        {
            document.getElementById("occupation").focus();
            $("#occupation_errmsg").html("Please Enter Occupation").show();
            return false
        }
        if (email == '')
        {
            document.getElementById("email").focus();
            $("#email_errmsg").html("Please Enter Email").show();
            return false
        }
        if (income == 'select_income')
        {
            document.getElementById("income").focus();
            $("#income_errmsg").html("Please Enter Income").show();
            return false
        }
        if (select_school == 'select_school')
        {
            document.getElementById("school_ids").focus();
            $("#school_ids_errmsg").html("Please Select School").show();
            return false
        }
        if (select_courses == '0')
        {
            document.getElementById("standard_ids").focus();
            $("#standard_ids_errmsg").html("Please Select Courses").show();
            return false
        }
        if (select_intake == 'select_intake')
        {
            document.getElementById("year_ids").focus();
            $("#year_ids_errmsg").html("Please Select Intake").show();
            return false
        }
        if (phone_no == '')
        {
            document.getElementById("phone_no").focus();
            $("#phone_no_errmsg").html("Please Enter Phone Number In General").show();
            $('#general_tab').css('background-color','red');
            return false
        }
        if (mobile_no == '')
        {
            document.getElementById("mobile_no").focus();
            $("#mobile_no_errmsg").html("Please Enter Mobile Number").show();
            $('#general_tab').css('background-color','red');
            return false
        }
        if (general_survey_val == 'select_general_survey')
        {
            document.getElementById("general_survey_id").focus();
            $("#general_survey_id_errmsg").html("Please Enter General Survey In general Survey").show();
            $('#general_survey_tab').css('background-color','red');
            return false
        }
        if (highest_qualification == 'select_highest_qualification')
        {
            document.getElementById("highest_qualification_id").focus();
            $("#highest_qualification_id_errmsg").html("Please Enter Highest Qualification").show();
            $('#education_background_tab').css('background-color','red');
            return false
        }
        if (select_courses == '')
        {
            if (eb_institution_val == '')
            {
                document.getElementById("eb_institution").focus();
                $("#eb_institution_errmsg").html("Please Enter Islamic Studies Highest Achievement").show();
                $('#education_background_tab').css('background-color','red');
                return false
            }
        }
        // if (eb_from_date_val == '')
        // {
        //     document.getElementById("eb_from_date").focus();
        //     $("#eb_institution_errmsg").html("Please Enter Islamic Studies Highest Achievement").show();
        //     $('#education_background_tab').css('background-color','red');
        //     return false
        // }
        // if (eb_to_date_val == '')
        // {
        //     document.getElementById("eb_to_date").focus();
        //     $("#eb_institution_errmsg").html("Please Enter Islamic Studies Highest Achievement").show();
        //     $('#education_background_tab').css('background-color','red');
        //     return false
        // }
        // if (eb_achievement_val == '')
        // {
        //     document.getElementById("eb_achievement").focus();
        //     $("#eb_institution_errmsg").html("Please Enter Islamic Studies Highest Achievement").show();
        //     $('#education_background_tab').css('background-color','red');
        //     return false
        // }
        if(dob)
        {
            if(age_month < 0 || (age_month == 0 && age_day <0)) {
                age = parseInt(age) -1;
            }
            if ((age == 15 && age_month <= 0 && age_day <=0) || age < 15)
            {
                document.getElementById("dob").focus();
                $("#dob_errmsg").html("Age should be greater than 15 years").show();
                return false                
            }
            else
            {
                $('#age').val(age);
            }
        }
        
        $('#declaration_form').modal('show');
    });
    
    $('#dob').datetimepicker(datepickers_options);
    $('#previous_school_admission_date').datetimepicker(datepickers_options);
    $('#previous_school_exit_date').datetimepicker(datepickers_options);
    
    $('#eb_to_date').datetimepicker(datepickers_options);
    $('#eb_from_date').datetimepicker(datepickers_options);
    
    $("#dob").change(function()
    {
        $("#dob_errmsg").hide()
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
                <input type="text" style="height:43px; width:350px;" class="form-control" name="eb_institution_'+total_line+'" id="eb_institution_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;" class="form-control" name="eb_from_date_'+total_line+'" id="eb_from_date_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;" class="form-control" name="eb_to_date_'+total_line+'" id="eb_to_date_'+total_line+'"/>\
            </td>\
            <td>\
                <input type="text" style="height:43px; width:350px;" class="form-control name="eb_achievement_'+total_line+'" id="eb_achievement_'+total_line+'"/>\
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
        $("#school_ids_errmsg").hide();
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
                    $("#standard_ids").html('');
                    $("#year_ids").html('');
                    $("#standard_ids").append("<option value='0'>Select Course</option>");
                    for ( i = 0; i<  data['standard_ids'].length; i++ )
                    {
                        $("#standard_ids").append("<option value='"+data['standard_ids'][i]['id']+"'>"+data['standard_ids'][i]['name']+"</option>");
                    }
                }
            }
        });
    });
});