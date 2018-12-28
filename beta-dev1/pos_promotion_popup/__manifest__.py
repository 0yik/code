# -*- coding: utf-8 -*-
{
    'name' : 'POS promotion Popup',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """POS Show Promotion Popup.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','pos_promotion','pos_promotion_multiselect'],
    'data': [
		'view/register.xml',
        'view/promotion.xml'
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
