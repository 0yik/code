# -*- coding: utf-8 -*-
{
    "name": "EMS Attendance Modifier",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''This module for the attendance modifier''',
    'summary': 'School Management',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','web_readonly_bypass','school_attendance','ems_class_classroom'],
    "data": [
		'views/ems_attendance_view.xml',
    ],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
