# -*- coding: utf-8 -*-
{
    'name' : 'POS PIN Number',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / Sang',
    'description': """POS PIN Number for Pizzhut.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_restaurant_kitchen', 'dine_in_pos_module', 'delivery_orders_kds', 'pos_modifier_order_return'],
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
