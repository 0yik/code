# -*- coding: utf-8 -*-
{
    'name' : 'POS Sarangoci Modifier Receipt',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Bipin Prajapati',
    'description': """ """,
    'website': 'www.hashmicro.com',
    'depends' : ['point_of_sale'],
    'data': [ 
        'views/template.xml',
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
