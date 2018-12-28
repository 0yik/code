# -*- coding: utf-8 -*-
{
    "name": "Make-Up Exams",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''Create a Make-Up Exam(conduct a new exam) for the student which are not present in the scheduled exam.''',
    'summary': 'Make-Up Exam',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','web_readonly_bypass','exam'],
    "data": [
    	'security/ir.model.access.csv',
    	'wizard/makeup_exam_wizard_view.xml',
    	'views/exam_view.xml',
	],
    "qweb": [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
