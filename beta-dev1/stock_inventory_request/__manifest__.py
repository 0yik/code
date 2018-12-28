# -*- coding: utf-8 -*-
{
    'name' : 'Stock Inventory Request',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Trivedi',
    'description': """
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
		'delivery', 'sale', 'account', 'stock', 'purchase',
		],
    'data': [
    'security/ir.model.access.csv',
	'data/ir_sequence_data_view.xml',
	'views/inventory_request.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
