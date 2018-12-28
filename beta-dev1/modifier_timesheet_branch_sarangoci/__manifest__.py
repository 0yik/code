# -*- coding: utf-8 -*-
{
    'name': "Modifier Timesheet Branch",

    'description': """
        Timesheet,Human Resources
    """,
    'author': 'HashMicro / Quy/ MP Technolabs - Purvi',
    'website': 'www.hashmicro.com',

    'category': 'timesheet',
    'version': '1.0',

    'depends': ['hr_timesheet_sheet','hr_timesheet_attendance',],

    # always loaded
    'data': [
        'views/hr_timesheet_sheet.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/timesheet.xml',],
    'demo': [],
}