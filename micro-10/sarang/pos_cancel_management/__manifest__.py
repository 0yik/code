# -*- coding: utf-8 -*-
{
    'name' : 'POS Oderline Cancel',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila, Purvi Pandya',
    'description': """This module intends to have a functionality of cancel management with PIN number.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale', 'pos_pin_number', 'pos_supervisor_pin',],
    'data': [ 
        'views/pos_restaurant_templates.xml',
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
