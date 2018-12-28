# -*- coding: utf-8 -*-
{
    'name' : 'POS All Free',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Purvi Pandya',
    'description': """This module intends to have a functionality of free order.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale',],
    'data': [ 
        'views/pos_all_free_template.xml',
        'views/pos_all_free_view.xml'
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
