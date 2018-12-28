# -*- coding: utf-8 -*-
{
    'name': "hilti_modifier_customer_booking",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "HILTI/Nitin",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer Booking',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'sales_team', 'hilti_modifier_company'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template.xml',
        'data/ir_sequence_data.xml',
        'wizard/tester_wizard_views.xml',
        'wizard/reconfirm_booking_views.xml',
        'wizard/reschedule_booking_view.xml',
        'views/anchor_views.xml',
        'views/customer_booking_admin_view_inherit.xml',
        'views/time_slot_views.xml',
        'views/templates.xml',
        'views/reminder_configuration_views.xml',
        
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],

    # only loaded in demonstration mode
}
