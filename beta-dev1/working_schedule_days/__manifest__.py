# -*- coding: utf-8 -*-
{
    'name': "working_schedule_days",

    'description': """
        Changes working schedule to be number of days
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','resource'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/resource_calendar_attendace_views.xml',
        'views/resource_calendar_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}