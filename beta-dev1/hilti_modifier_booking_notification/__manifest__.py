# -*- coding: utf-8 -*-
{
    'name': "hilti_modifier_booking_notification",

    'summary': """
        This module sents notification of bookings.""",

    'description': """
        
    """,

    'author': "HILTI/Mustafa Kantawala",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project Booking',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hilti_modifier_tester_myrequests', 'hilti_reusable_user_respartner_changepassword'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/hashmicro_website_data.xml',
        'data/booking_cancel_email_templates.xml',
        'data/booking_customer_feedback_mail_templates.xml',
        'data/booking_delay_mail_templates.xml',
        'data/booking_details_mail_template.xml',
        'data/booking_reconfirmation_mail_templates.xml',
        'data/booking_reschedule_mail_templates.xml',
        'data/manual_reschedule_email_templates.xml',
        'data/tester_reminder_email_templates.xml',
        'data/tester_request_mail_templates.xml',
        'data/booking_reminder_reconfirmation_mail_templates.xml',
        'data/new_registration_email_template.xml',
        'data/tester_request_cancel_mail_templates.xml',
        'data/tester_request_unavailability_approved_mail_templates.xml',
        'data/dedicated_booking_mail_template.xml',
        'data/booking_dedicated_mail_templates.xml',
        'data/booking_cron.xml',
        'data/delayed_customer_booking_mail_templates.xml',
        'data/booking_swap_mail_template.xml',
        'wizard/tester_wizard_views.xml',
        'views/project_booking.xml',
        'views/reminder_notification_view.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
