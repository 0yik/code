# -*- coding: utf-8 -*-
{
    "name": "Make-Up Classes",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''Allow admin to add students in classes to mark to attendance. Add a list of students in the class form view of based on the students enrolled in that selected Intak, and allow to Add an Item. When marking attendance of the class, the students will be pulled from that class form view.''',
    'summary': 'Pro-Rate Fee',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','web_readonly_bypass','school_attendance','ems_class_classroom','ems_attendance'],
    "data": [
    	'security/ir.model.access.csv',
    	'views/ems_class_view.xml',
	],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
