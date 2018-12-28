# -*- coding: utf-8 -*-
{
    'name' : 'POS Supervisor PIN',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Purvi Pandya',
    'description': """This module intends to have functionality of varify PIN of 
    supervisor of the system to perform several functions.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale', 'pos_pin_number'],
    'data': [ 
        'data/group_data.xml',
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
