# -*- coding: utf-8 -*-
{
    'name': "Leave Auto Allocation",
    'description': """
        Leave Auto Allocation
    """,
    'author': "HashMicro/ MPTechnolabs(Chankya)",
    'website': "http://www.hashmicro.com",

    'category': 'hr',
    'version': '1.0',
    'depends': ['base', 'hr_leave_balance','sg_leave_extended', 'sg_holiday_extended'],
    # always loaded
    'data': [
        'views/sg_leave_extended_view.xml',
        'data/timesheet_cron_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}