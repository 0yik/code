$(document).ready(function() {
    function disableBack()
    { 
        window.history.forward()
    }        
    window.onload = disableBack();
    window.onpageshow = function(evt)
    {
        if (evt.persisted) disableBack() 
    }
    window.onload = disableBack();    
});

odoo.define('online_school_enrollment', function (require) {
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

    $("#first_name").keypress(function (e)
    {
        $("#full_name_errmsg").hide();
    });
    
    $("#address1").keypress(function (e)
    {
        $("#address1_errmsg").hide();
    });
    $("#address2").keypress(function (e)
    {
        $("#address2_errmsg").hide();
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
    
    $("#standard_ids").change(function()
    {
        $("#standard_ids_errmsg").hide();
    });
    $("#year_ids").change(function()
    {
        $("#year_ids_errmsg").hide();
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

    $(".open_declaration_form_button").click(function(){
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
        var email = document.getElementById("email").value
        var address1 = document.getElementById("address1").value
        var address2 = document.getElementById("address2").value
        var phone_no = document.getElementById("phone_no").value
        var mobile_no = document.getElementById("mobile_no").value
        var select_school = document.getElementById("school_ids").value
        var select_courses = document.getElementById("standard_ids").value
        var select_intake = document.getElementById("year_ids").value
        
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
        if (email == '')
        {
            document.getElementById("email").focus();
            $("#email_errmsg").html("Please Enter Email").show();
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
    
    // $('#eb_to_date').datetimepicker(datepickers_options);
    // $('#eb_from_date').datetimepicker(datepickers_options);
    
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