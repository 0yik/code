# -*- coding: utf-8 -*-
{
    'name': "HR GPS Attendance",
    'description': """
        HR GPS Attendance
    """,
    'author': "HashMicro / MpTechnolabs - Bipin Prajapati",
    'website': "http://www.hashmicro.com",
    'category': 'HashMicro',
    'version': '1.0',
    'depends': ['web', 'hr_attendance', 'partner_geo_map_location', 'web_map'],
    # always loaded
    'data': [
        'templates/assets.xml',
        'views/attendance_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
