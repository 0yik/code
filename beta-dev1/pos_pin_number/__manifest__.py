# -*- coding: utf-8 -*-
{
    'name' : 'POS PIN Number',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """POS PIN Number.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_restaurant_kitchen'],
    'data': [
	'view/template.xml',
	'view/res_users_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
