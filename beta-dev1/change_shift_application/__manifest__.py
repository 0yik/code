# -*- coding: utf-8 -*-
{
    'name': "change_shift_application",

    'description': """
        Allow employees to change shift with another employee by extending on multiple_leave_application module
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','multiple_leave_application', 'resource', 'working_schedule_days'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays_views.xml',
        'views/hr_holidays_multiple_view.xml',
        'data/data.xml',
        'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}