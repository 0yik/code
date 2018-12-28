# -*- coding: utf-8 -*-
{
    "name": "Assign Substitute Teacher",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''This module help to assign substitute teacher if any teacher absent for the particular class and send a email notification for to the substitute teacher.''',
    'summary': 'Substitute Teacher for Class',
    "website": "www.hashmicro.com",
    "category": "Substitute Teacher",
    "depends": ['school','school_attendance','ems_class_classroom','web_readonly_bypass','sg_hr_holiday'],
    "data": [
		'data/ir_config_parameter_data.xml',
		'wizard/substitute_wizard_view.xml',
		'views/daily_attendance_view.xml',
		'views/hr_leave_config_view.xml',
    ],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
