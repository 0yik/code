# -*- coding: utf-8 -*-
{
    'name': "HR GPS Attendance Radius",
    'description': """
        HR GPS Attendance Radius
    """,
    'author': "HashMicro / MpTechnolabs - Bipin Prajapati",
    'website': "http://www.hashmicro.com",
    'category': 'HashMicro',
    'version': '1.0',
    'depends': ['web','hr_attendance','hr_gps_attendance', 'branch','hr', 'hr_timesheet_attendance'],
    # always loaded
    'data': [
        'templates/assets.xml',
        'views/branch_view.xml',
        'views/company_view.xml',
        'views/attendance_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
