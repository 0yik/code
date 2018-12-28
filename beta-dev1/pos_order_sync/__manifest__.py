# -*- coding: utf-8 -*-
{
    'name' : 'POS Order Sync',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Bhavin Jethva',
    'description': """Sync POS Order to one to another Server.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['point_of_sale'],
    'data': [
	'views/pos_order_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
