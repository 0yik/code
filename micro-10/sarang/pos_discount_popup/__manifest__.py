# -*- coding: utf-8 -*-
{
    'name' : 'POS Show Discount Popup',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / MP technolabs / Parikshit Vaghasiya / Viet',
    'description': """POS Show Discount Popup.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale'],
    'data': [
		'view/pos_show_discount_view.xml', 
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
