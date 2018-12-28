# -*- coding: utf-8 -*-
{
    "name": "Pro-Rate Fee",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''Pro-Rate Fee (This is for Monthly Fee and Semester Fee)''',
    'summary': 'Pro-Rate Fee',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','web_readonly_bypass','school_fees','semester_fees_receipt_ems','ems_class_classroom'],
    "data": [
    	'demo/fees_structure.xml',
    	'views/student_fees_structure_line_view.xml',
	],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
