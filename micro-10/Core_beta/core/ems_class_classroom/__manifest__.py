# -*- coding: utf-8 -*-
{
    "name": "EMS Class - Classroom",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''This module for the EMS Class and Classroom functionality''',
    'summary': 'School Management',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','web_readonly_bypass','sg_hr_holiday'],
    "data": [
		'security/ir.model.access.csv',
		'views/ems_classroom_view.xml',
		'views/ems_class_view.xml',
    ],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
