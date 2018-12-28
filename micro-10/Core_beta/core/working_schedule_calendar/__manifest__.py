# -*- coding: utf-8 -*-
{
    'name': "working_schedule_calendar",

    'description': """
        Develop calendar view for working schedule.
    """,

    'author': "'HashMicro / MP technolabs / Prakash',",
    'website': 'https://www.hashmicro.com',

    
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract','hr_holidays','calendar','resource','sg_hr_employee'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

