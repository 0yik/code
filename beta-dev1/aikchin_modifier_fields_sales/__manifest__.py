# -*- coding: utf-8 -*-
{
    'name' : 'Aikchin Modifier Fields (sales)',
    'version' : '1.0',
    'category': 'HR',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Modify the fields for Sales module.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sale', 'account', 'delivery', 'multiple_customer_delivery_address'],
    'data': [
		'view/sale_order_view.xml',
		'view/res_partner_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
