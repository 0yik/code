# -*- coding: utf-8 -*-
{
    'name' : 'POS Receipt Reprint',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """POS Receipt Reprint.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_restaurant_kitchen'],
    'data': [
	'view/template.xml',
	#'view/res_users_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/pos_reprint_button.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
