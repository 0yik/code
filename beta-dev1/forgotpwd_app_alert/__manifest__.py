# -*- coding: utf-8 -*-
{
    'name': "forgotpwd_app_alert",
    'summary': """
        Forgot Password Customization""",
    'description': """
        Using this module, users will receive an alert once the password is reset using the base module functionality of sending mail to the user and using the link in the mail to reset the password.

Instead of logging in the user to the web, alert will display the message of successful reset and then ask the user to login to the app using the new password.
    """,

    'author': "Soundarya",
    'website': "http://www.biocare.com",
    'category': 'Base',
    'version': '0.1',
    'depends': ['auth_signup'],
    'data': [
        "security/groups.xml",
        "views/website_templates.xml",
    ],
}