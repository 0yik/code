# -*- coding: utf-8 -*-
{
    'name' : 'PDP Attendance',
    'version' : '1.0',
    'category': 'Point of Sale',
    'author': 'HashMicro / MP technolabs(Chankya Soni)',
    'description': """
	You can create attendance from pos session.
    """,
    'website': 'www.hashmicro.com',
    'depends' : [
	'point_of_sale','hr_attendance'
    ],
    'data': [
        '__import__/template.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/pos_attendance.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
