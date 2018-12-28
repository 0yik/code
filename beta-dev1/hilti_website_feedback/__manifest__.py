# -*- coding: utf-8 -*-
{
    'name': "Hilti Website Feedback",

    'summary': """
        Feedback for Project booking""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HILTI/Mustufa",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Partner-Company',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hilti_modifier_booking_notification'],

    # always loaded
    'data': [
        'data/mail_template.xml',
        'wizard/booking_feedback.xml',
        'views/project_booking.xml',
        'views/website_template.xml',
    ],
    # only loaded in demonstration mode
}