$(document)
    .ready(
        function() {

            $('.sign_up_custom').click(
                function() {
                    var check_validate_login = true
                    var password = $(
                        ".oe_login_form input#password").val();
                    var login = $(".oe_login_form input#login")
                        .val();
                    if (login) {
                        $('.email_validation_blanck').css(
                            'display', 'none');
                    } else {
                        $('.email_validation_blanck').css(
                            'display', 'block');
                        check_validate_login = false;
                    }

                    if (password) {
                        $('.email_validation_blanck_password').css(
                            'display', 'none');
                    } else {
                        $('.email_validation_blanck_password').css(
                            'display', 'block');
                        check_validate_login = false;
                    }

                    if (check_validate_login == true) {
                        return true;
                    } else {
                        return false;
                    }

                });

            $('.registerd_button')
                .click(
                    function() {
                        var check_validate = true
                        var password = $(
                                ".oe_signup_form input#password")
                            .val();
                        var con_password = $(
                                ".oe_signup_form input#confirm_password")
                            .val();
                        var login = $(
                                ".oe_signup_form input#login")
                            .val();
                        var account_number = $(
                                ".oe_signup_form input#account_number")
                            .val();
                        var name = $(
                                ".oe_signup_form input#name")
                            .val();
                        if (login) {
                            validateEmail(login);
                            $('.email_validation_bl_re').css(
                                'display', 'none');
                        } else {
                            $('.email_validation_bl_re').css(
                                'display', 'block');
                            check_validate = false;
                        }

                        if (password) {
                            $('.password_validation_bl_re')
                                .css('display', 'none');
                            if (password.length < 6) {
                                $(
                                        '.password_validation_character_total')
                                    .css('display', 'block');
                                check_validate = false;
                            } else {
                                $(
                                        '.password_validation_character_total')
                                    .css('display', 'none');
                                if (password
                                    .match(/([a-zA-Z])/) &&
                                    password
                                    .match(/([0-9])/)) {
                                    $(
                                            '.password_validation_character')
                                        .css('display',
                                            'none');
                                } else {
                                    check_validate = false;
                                    $(
                                            '.password_validation_character')
                                        .css('display',
                                            'block');
                                }
                            }
                        } else {
                            $('.password_validation_bl_re')
                                .css('display', 'block');
                            check_validate = false;
                        }

                        if (con_password) {
                            $('.repassword_validation_bl_re')
                                .css('display', 'none');
                        } else {
                            $('.repassword_validation_bl_re')
                                .css('display', 'block');
                            check_validate = false;
                        }
                        if (name) {
                            $('.name_validation_bl_re').css(
                                'display', 'none');
                        } else {
                            $('.name_validation_bl_re').css(
                                'display', 'block');
                            check_validate = false;
                        }

                        if (con_password && password) {
                            if (password != con_password) {
                                $('.pass_validation').css(
                                    'display', 'block');
                                check_validate = false;
                            } else {
                                $('.pass_validation').css(
                                    'display', 'none');
                            }
                        }
                        if (account_number) {
                            $('.acc_validation_bl_re').css(
                                'display', 'none');
                            if ($.isNumeric(account_number)) {
                                $('.acc_validation').css(
                                    'display', 'none');
                                if ($(
                                        ".oe_signup_form input#account_number")
                                    .val().length != 8) {
                                    $('.acc_validation_digit')
                                        .css('display',
                                            'block');
                                    check_validate = false;
                                } else {
                                    $('.acc_validation_digit')
                                        .css('display',
                                            'none');
                                }
                            } else {
                                $('.acc_validation').css(
                                    'display', 'block');
                                check_validate = false;
                            }
                        } else {
                            $('.acc_validation_bl_re').css(
                                'display', 'block');
                            check_validate = false;
                        }

                        if (check_validate == true) {
                            return true;
                        } else {
                            return false;
                        }

                        function validateEmail(email) {
                            var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
                            if (!emailReg.test(email)) {
                                $('.email_validation').css(
                                    'display', 'block');
                                check_validate = false;
                            } else {
                                $('.email_validation').css(
                                    'display', 'none');
                            }
                        }
                    });

            $('.oe_login_form input.form-control')
                .each(
                    function() {
                        $(this)
                            .keyup(
                                function() {
                                    var complete = true;
                                    $(
                                            '.oe_login_form input.form-control')
                                        .each(
                                            function() {
                                                if (!$(
                                                        this)
                                                    .val()) {
                                                    complete = false;
                                                }
                                                if (this.name == 'password') {
                                                    if ($(
                                                            this)
                                                        .val()) {
                                                        $(
                                                                '.email_validation_blanck_password')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_login_form input#login")
                                                        .val()) {
                                                        $(
                                                                '.email_validation_blanck')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_blanck')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                }
                                            });
                                    if (complete == true) {
                                        $(
                                                '.custom_button_login')
                                            .css(
                                                'opacity',
                                                '1');
                                    } else {
                                        $(
                                                '.custom_button_login')
                                            .css(
                                                'opacity',
                                                '0.5');
                                    }
                                });

                    });

            $('.open_tool_tip').tooltip('destroy');
            $('.open_tool_tip').tooltip({
                placement: 'left'
            });

            /*
             * $('.oe_login_form input.open_tool_tip').tooltip({
             * placement: "left", trigger: "focus", });
             */

            $('.oe_signup_form input.form-control')
                .each(
                    function() {
                        /*
                         * $('.oe_signup_form
                         * input.form-controll-boolean').click(function () {
                         * if ($(this).is(':checked')) {
                         * $('.hide_show_account').css('display',
                         * 'block');
                         * $('.form-test').addClass('form-control'); }
                         * else {
                         * $('.hide_show_account').css('display',
                         * 'none');
                         * $('.form-test').removeClass('form-control'); }
                         * });
                         */
                        $(this)
                            .change(
                                function() {
                                    if (this.name == 'name') {
                                        if ($(this)
                                            .val()) {
                                            $(
                                                    '.name_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'none');
                                        } else {
                                            $(
                                                    '.name_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                    }
                                    if (this.name == 'login') {
                                        var email = $(
                                                this)
                                            .val();
                                        if (email) {
                                            validateEmail(email);
                                            $(
                                                    '.email_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'none');
                                        } else {
                                            $(
                                                    '.email_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                    }
                                    if (this.name == 'password') {
                                        $(
                                                ".oe_signup_form input#confirm_password")
                                            .val('');
                                        if ($(this)
                                            .val()) {
                                            $(
                                                    '.password_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'none');
                                        } else {
                                            $(
                                                    '.password_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                        if ($(this)
                                            .val().length < 6) {
                                            $(
                                                    '.password_validation_character_total')
                                                .css(
                                                    'display',
                                                    'block');
                                        } else {
                                            $(
                                                    '.password_validation_character_total')
                                                .css(
                                                    'display',
                                                    'none');
                                            if ($(this)
                                                .val()
                                                .match(
                                                    /([a-zA-Z])/) &&
                                                $(
                                                    this)
                                                .val()
                                                .match(
                                                    /([0-9])/)) {
                                                $(
                                                        '.password_validation_character')
                                                    .css(
                                                        'display',
                                                        'none');
                                            } else {
                                                $(
                                                        '.password_validation_character')
                                                    .css(
                                                        'display',
                                                        'block');
                                            }
                                        }
                                    }
                                    if (this.name == 'confirm_password') {
                                        var copass = $(
                                                this)
                                            .val();
                                        if (copass) {
                                            $(
                                                    '.repassword_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'none');
                                        } else {
                                            $(
                                                    '.repassword_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                        var password = $(
                                                ".oe_signup_form input#password")
                                            .val();
                                        if (password &&
                                            copass) {
                                            if (password != copass) {
                                                $(
                                                        '.pass_validation')
                                                    .css(
                                                        'display',
                                                        'block');
                                            } else {
                                                $(
                                                        '.pass_validation')
                                                    .css(
                                                        'display',
                                                        'none');
                                            }
                                        }

                                    }
                                    if (this.name == 'account_number') {
                                        var acc_no = $(
                                                this)
                                            .val();
                                        if (acc_no) {
                                            $(
                                                    '.acc_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'none');
                                        } else {
                                            $(
                                                    '.acc_validation_bl_re')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                        if ($
                                            .isNumeric(acc_no)) {
                                            $(
                                                    '.acc_validation')
                                                .css(
                                                    'display',
                                                    'none');
                                            if ($(this)
                                                .val().length != 8) {
                                                $(
                                                        '.acc_validation_digit')
                                                    .css(
                                                        'display',
                                                        'block');
                                            } else {
                                                $(
                                                        '.acc_validation_digit')
                                                    .css(
                                                        'display',
                                                        'none');
                                            }
                                        } else {
                                            $(
                                                    '.acc_validation')
                                                .css(
                                                    'display',
                                                    'block');
                                        }
                                    }

                                });

                        function validateEmail(email) {
                            var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
                            if (!emailReg.test(email)) {
                                $('.email_validation').css(
                                    'display', 'block');
                            } else {
                                $('.email_validation').css(
                                    'display', 'none');
                            }
                        }

                        $(this)
                            .keyup(
                                function() {
                                    var complete = true;
                                    $(
                                            '.oe_signup_form input.form-control')
                                        .each(
                                            function() {
                                                // For
                                                // all
                                                // field
                                                // validation

                                                // key
                                                // up
                                                // event
                                                if (!$(
                                                        this)
                                                    .val()) {
                                                    complete = false;
                                                }
                                                if (this.name == 'name' &&
                                                    $(
                                                        ".oe_signup_form input#name")
                                                    .val()) {
                                                    if (!$(
                                                            ".oe_signup_form input#login")
                                                        .val()) {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                }
                                                if (this.name == 'password' &&
                                                    $(
                                                        ".oe_signup_form input#password")
                                                    .val()) {
                                                    if (!$(
                                                            ".oe_signup_form input#login")
                                                        .val()) {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#name")
                                                        .val()) {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if ($(
                                                            this)
                                                        .val().length < 6) {
                                                        $(
                                                                '.password_validation_character_total')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.password_validation_character_total')
                                                            .css(
                                                                'display',
                                                                'none');
                                                        if ($(
                                                                this)
                                                            .val()
                                                            .match(
                                                                /([a-zA-Z])/) &&
                                                            $(
                                                                this)
                                                            .val()
                                                            .match(
                                                                /([0-9])/)) {
                                                            $(
                                                                    '.password_validation_character')
                                                                .css(
                                                                    'display',
                                                                    'none');
                                                        } else {
                                                            $(
                                                                    '.password_validation_character')
                                                                .css(
                                                                    'display',
                                                                    'block');
                                                        }
                                                    }

                                                }
                                                if (this.name == 'confirm_password' &&
                                                    $(
                                                        ".oe_signup_form input#confirm_password")
                                                    .val()) {
                                                    if (!$(
                                                            ".oe_signup_form input#login")
                                                        .val()) {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#name")
                                                        .val()) {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#password")
                                                        .val()) {
                                                        $(
                                                                '.password_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.password_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                }
                                                if (this.name == 'account_number' &&
                                                    $(
                                                        ".oe_signup_form input#account_number")
                                                    .val()) {
                                                    if (!$(
                                                            ".oe_signup_form input#login")
                                                        .val()) {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#name")
                                                        .val()) {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.name_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#password")
                                                        .val()) {
                                                        $(
                                                                '.password_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.password_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                    if (!$(
                                                            ".oe_signup_form input#confirm_password")
                                                        .val()) {
                                                        $(
                                                                '.repassword_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.repassword_validation_bl_re')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                }
                                            });
                                    if (complete == true) {
                                        $(
                                                '.custom_button_login')
                                            .css(
                                                'opacity',
                                                '1');
                                    } else {
                                        $(
                                                '.custom_button_login')
                                            .css(
                                                'opacity',
                                                '0.5');
                                    }
                                });

                    });

            $('.custom_reset_button')
                .click(
                    function() {
                        var check_validate1 = true;
                        if (!$(
                                ".oe_reset_password_form input#login")
                            .val()) {
                            $('.email_validation_bl_re_reset')
                                .css('display', 'block');
                            check_validate1 = false;
                        } else {
                            $('.email_validation_bl_re_reset')
                                .css('display', 'none');
                            validateEmail($(
                                    ".oe_reset_password_form input#login")
                                .val());
                        }

                        function validateEmail(email) {
                            var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
                            if (!emailReg.test(email)) {
                                $('.email_validation_reset')
                                    .css('display', 'block');
                                check_validate1 = false;
                            } else {
                                $('.email_validation_reset')
                                    .css('display', 'none');
                            }
                        }
                        if (check_validate1 == true) {
                            return true;
                        } else {
                            return false;
                        }

                    });

            $('.oe_reset_password_form input.form-control')
                .each(
                    function() {
                        $(this).change(function() {
                            if (this.name == 'login') {
                                var email = $(this).val();
                                validateEmail(email);
                            }
                        });

                        function validateEmail(email) {
                            var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
                            if (!emailReg.test(email)) {
                                $('.email_validation_reset')
                                    .css('display', 'block');
                            } else {
                                $('.email_validation_reset')
                                    .css('display', 'none');
                            }
                        }

                        $(this)
                            .keyup(
                                function() {
                                    var complete = true;
                                    $(
                                            '.oe_reset_password_form input.form-control')
                                        .each(
                                            function() {
                                                if (!$(
                                                        this)
                                                    .val()) {
                                                    complete = false;
                                                }
                                                if (this.name == 'login') {
                                                    if (!$(
                                                            this)
                                                        .val()) {
                                                        $(
                                                                '.email_validation_bl_re_reset')
                                                            .css(
                                                                'display',
                                                                'block');
                                                    } else {
                                                        $(
                                                                '.email_validation_bl_re_reset')
                                                            .css(
                                                                'display',
                                                                'none');
                                                    }
                                                }
                                            });
                                    if (complete == true) {
                                        $(
                                                '.custom_reset_button')
                                            .css(
                                                'opacity',
                                                '1');
                                    } else {
                                        $(
                                                '.custom_reset_button')
                                            .css(
                                                'opacity',
                                                '0.5');
                                    }
                                });

                    });

        });

$(window, document, undefined)
    .ready(
        function() {

            $('input').blur(function() {
                var $this = $(this);
                if ($this.val())
                    $this.addClass('used');
                else
                    $this.removeClass('used');
            });

            var $ripples = $('.ripples');

            $ripples.on('click.Ripples', function(e) {

                var $this = $(this);
                var $offset = $this.parent().offset();
                var $circle = $this.find('.ripplesCircle');

                var x = e.pageX - $offset.left;
                var y = e.pageY - $offset.top;

                $circle.css({
                    top: y + 'px',
                    left: x + 'px'
                });

                $this.addClass('is-active');

            });

            $ripples
                .on(
                    'animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd',
                    function(e) {
                        $(this).removeClass('is-active');
                    });
            $('select').blur(function() {
                var $this = $(this);
                if ($this.val())
                    $this.addClass('used');
                else
                    $this.removeClass('used');
            });


            var $ripples = $('.ripples');

            $ripples.on('click.Ripples', function(e) {

                var $this = $(this);
                var $offset = $this.parent().offset();
                var $circle = $this.find('.ripplesCircle');

                var x = e.pageX - $offset.left;
                var y = e.pageY - $offset.top;

                $circle.css({
                    top: y + 'px',
                    left: x + 'px'
                });

                $this.addClass('is-active');

            });

            $ripples
                .on(
                    'animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd',
                    function(e) {
                        $(this).removeClass('is-active');
                    });

        });