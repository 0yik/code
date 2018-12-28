# -*- coding: utf-8 -*-
{
    'name' : 'Stock Inventory Request',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
		'delivery', 'sale', 'account', 'stock', 'purchase','web_readonly_bypass', 'task_list_manager'
		],
    'data': [
    'security/ir.model.access.csv',
    'security/security_groups.xml',
	'data/ir_sequence_data_view.xml',
    'views/stock_picking.xml',
	'views/inventory_request.xml',
	'views/return_request.xml',
	'views/tester_request.xml',
	'views/master_reason.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
