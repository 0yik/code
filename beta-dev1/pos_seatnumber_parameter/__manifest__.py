# -*- coding: utf-8 -*-
{
    'name' : 'pos_seatnumber_parameter',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Duy',
    'description': """pos_seatnumber_parameter.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','dine_in_pos_module'],
    'data': [
		'view/seat_number.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
