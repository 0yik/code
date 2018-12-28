# -*- coding: utf-8 -*-
{
    'name' : 'POS Transfer Confirmation',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila',
    'description': """On POS display a confirm message box for Transfer table.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_restaurant'],
    'data': [
		'views/pos_registration.xml', 
    ],
    'demo': [
    ],
    'qweb': [
	# 'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
