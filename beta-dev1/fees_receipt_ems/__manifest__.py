# -*- coding: utf-8 -*-
{
    "name": "Customization In Pergas School Management",
    "author": "HashMicro/ Amit Patel",
    "version": "1.0",
    'description': '''
    	1/ Move student to another courses and school
    	2/ Create a Fee Receipt at the time of the studnet enrolment and confirm that enrolment
    	3/ Create a monthly draft receipt from the Fee Register.
    	4/ Update the Student History based upon his passing the courses
    	5/ Add age validation at the time of Student creation.
    	6/ Automatic filling the Courses,Terms, Level, Medium and based upon the Intake.
    ''',
    'summary': 'School Management Customization',
    "website": "www.hashmicro.com",
    "category": "School Management",
    "depends": ['school','school_attendance','school_fees'],
    "data": [
		'security/ir.model.access.csv',
		'wizard/move_courses_view.xml',
		'views/school_extended_view.xml',
    ],
    "qweb": [],
    'demo': ['demo/school_fees_demo.xml'],
    'installable': True,
    'auto_install': False,
}
