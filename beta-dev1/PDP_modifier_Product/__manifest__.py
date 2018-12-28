# -*- coding: utf-8 -*-
{
    'name' : 'PDP Modifier Product',
    'version' : '1.0',
    'category': 'Product',
    'author': 'HashMicro / MP technolabs / Monali',
    'description': """
	Add new field into new product menu.
    """,
    'website': 'www.hashmicro.com',
    'depends' : [
	'product','sales_team'
    ],
    'data': [
    'data/product_data.xml',
	'views/brand_view.xml',
	'views/product_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
