# -*- coding: utf-8 -*-
{
    'name' : 'Sale Invetory View',
    'version' : '1.0',
    'category': 'Product',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'sale', 'sales_team', 'account', 'procurement', 'stock', 'warehouse_modifier_shop'
    ],
    'data': [
    'views/sale_order.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
