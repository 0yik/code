# -*- coding: utf-8 -*-
{
    'name': "Leave Multi Approval Levels",

    'summary': """
        Leave multi approval & rejection management.""",

    'description': """
        Leave multi approval & rejection management.
    """,

    'author': "HashMicro",
    'website': "http://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_holidays', 'sg_hr_employee', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/hr_holiday_view.xml',
        'views/leave_approval_view.xml',
        
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
