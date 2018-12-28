# -*- coding: utf-8 -*-
{
    'name': "pos_customers_hoax",
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """Pos customer hoax 
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','pos_loyalty'],
    'data': [
		'views/views.xml',
        'views/templates.xml'
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
    'installable' : True
}